import pysam
import argparse
import re
from operator import itemgetter
from collections import defaultdict
import pandas as pd

def clin_msi_argparser():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--input-file', type=str, required=True)
    parser.add_argument('--bam', type=str, required=True)
    parser.add_argument('--reference', type=str, required=True)
    parser.add_argument('--output-dir', type=str, required=True, help="")
    parser.add_argument('--allow_mismatch', action='store_true')

    return parser

def repetitions(s):
    #Taken from https://stackoverflow.com/questions/9079797/detect-repetitions-in-string
    r = re.compile(r"(.+?)\1+")
    for match in r.finditer(s):
        yield (match.group(1), len(match.group(0))/len(match.group(1)))

def parse_input_file(input_file):
    location_list = []
    open_file = open(input_file, 'r')
    for line in open_file:
        chr, start, stop = line.split('\t')
        location_list.append([str(chr), int(start), int(stop)])

    return location_list

def clin_msi():
    parser = clin_msi_argparser()
    args = parser.parse_args()

    msi_location_list = parse_input_file(args.input_file)

    bam_file = pysam.AlignmentFile(args.bam, "rb")
    df = pd.DataFrame()

    for chr, start, stop in msi_location_list:
        length_dict = defaultdict(int)
        fasta_seq = pysam.faidx(args.reference, f"{chr}:{start-10}-{stop+10}").split('\n')[1]
        rep_list = list(repetitions(fasta_seq))
        print(rep_list)
        largest_rep_unit = max(rep_list, key=itemgetter(1))[0]
        largest_rep_len = int(max(rep_list, key=itemgetter(1))[1])
        print(largest_rep_len, largest_rep_unit)
        get_flanks = re.search(fr"(\w{{5}}){largest_rep_unit}{{{largest_rep_len}}}(\w{{5}})", fasta_seq)
        left_flank = get_flanks.group(1)
        right_flank = get_flanks.group(2)

        print(left_flank, fasta_seq, right_flank)


        for read in bam_file.fetch(chr, start-500, stop+500):
            if read.is_duplicate:
                continue
            if read.is_unmapped:
                continue
            if read.mapping_quality < 1:
                continue
            if read.reference_start > start:
                continue

            difference = start - read.reference_start
            #print(re_string)
            read_wo_softclip = read.query_sequence[read.query_alignment_start:read.query_alignment_end]
            get_rep = re.search(fr"{left_flank}({largest_rep_unit}+){right_flank}", read_wo_softclip)
            if args.allow_mismatch:
                get_rep = re.search(fr"{left_flank}({largest_rep_unit}+[ACTG]?{largest_rep_unit}+){right_flank}", read_wo_softclip)
            if get_rep is None:
                continue
            length_dict[len(get_rep.group(1))] += 1

        length_list = ['N-10', 'N-9', 'N-8', 'N-7', 'N-6', 'N-5', 'N-4', 'N-3', 'N-2', 'N-1', 'N',
                       'N+1', 'N+2', 'N+3', 'N+4', 'N+5', 'N+6', 'N+7', 'N+8', 'N+9', 'N+10']
        repeat_count_list = []
        for x in range(largest_rep_len - 10, largest_rep_len + 11):
            if not length_dict[x]:
                length_dict[x] = 0
            repeat_count_list.append(length_dict[x])

        df['Repeat_Length'] = length_list
        df[f'{chr}:{start}-{stop}'] = repeat_count_list
            #print(f'rep len: {x}, nubmer of reads:{length_dict[x]}')

    df.to_csv('test.csv', index=False)


if __name__ == '__main__':
    clin_msi()