
"""
        How to use
------------------------------
Python version = 3.7

python parseRaw.py example_raw_data.xlsx

example_raw_data.xlsx = path to the raw output generated by Patrick's Scripts

Should take < 1 minutes to run

"""

import argparse
import pandas as pd
import numpy as np



def feature_mean_std(repeat_df, sample_name):
	std = repeat_df.std(axis=0)
	u = repeat_df.mean(axis=0)
	std.index = std.index + '_std'
	u.index = u.index + '_u'
	single_sample_df = pd.DataFrame(pd.concat([u, std]).T,columns=[sample_name]).T
	return single_sample_df

def normalizeZscore(repeat_df, sample_name):
	mu = repeat_df.mean(axis=0)
	std = repeat_df.std(axis=0)
	df_data = (repeat_df.iloc[:, 1:] - mu) / std # ignore repeat_length column
	df_data.fillna(0, inplace=True)
	# turn this into a single sample and add the proper feature names
	raveled_data = df_data.T.values.ravel()
	#print(df_data)
	columns = np.tile(repeat_df['Repeat_Length']+'_',df_data.shape[1]) + np.repeat(df_data.columns,df_data.shape[0])
	single_sample_df = pd.DataFrame(raveled_data.reshape(1,-1),columns=columns ,index=[sample_name])	
	return single_sample_df

def parse_raw_data(repeat_df, sample_name, norm='z'):

	# check to make sure input is a dataframe
	assert type(repeat_df) is pd.core.frame.DataFrame, "Invalid input, must be a pandas dataframe object"

	# make sure we have an expected column

	assert repeat_df.columns[0] == 'Repeat_Length', "Repeat dataframe is missing an expected column, Repeat_Length"

	# choose a normalization scheme
	if norm == 'z':
		single_sample_df = normalizeZscore(repeat_df, sample_name)
		return single_sample_df
	elif norm == 'std_u':
		single_sample_df = feature_mean_std(repeat_df, sample_name)
		return single_sample_df
	# save the df
	# final_output = '/'.join(path.split('/')[:-1])+'/zscore_normalized_{}.csv'.format(sample_name)
	# marker_design_matrix.to_csv(final_output)

def main():
	parser = argparse.ArgumentParser(prog='Parse raw MSI data',description='Convert an excel file into a design matrix for machine learning with the markers zscore normalized by row')
	parser.add_argument('repeat_df', type=pd.core.frame.DataFrame, nargs=1, help='pandas dataframe holding a single sample')
	# parser.add_argument('path', metavar='/path/to/zscore/normalized/msi/data/sample.xlsx', type=str, nargs=1, help='path to the test data must be in excel or csv format')
	parser.add_argument('sample_name', metavar='XXXX', type=str, nargs=1, help='name of sample', default='test_sample')
	args = parser.parse_args()
	parse_raw_data(args.repeat_df, args.sample_name)

if __name__ == '__main__':
    main()
