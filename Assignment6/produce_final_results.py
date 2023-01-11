import csv
import matplotlib.pyplot as plt
import os
import re
import ReadConfig
import pandas as pd

config = ReadConfig.get_config()
file_path = config['storage_location']

def read_csv_to_df(file, header):
    """
    Read csv file without header and add a custom header.
    :param:
        file: path to file and filename
        header: custom list of headers
    :return:
        df: resulting dataframe
    """
    headers = header
    df = pd.read_csv(file, delimiter= '|', header = None, names = headers)
    return df


def concat_df(header, file_list):
    """
    Concatenate all dataframes that
    """
    old_df = pd.DataFrame(columns = header)
    for file in file_list:
        df = read_csv_to_df(file)
        new_df = pd.concat([old_df, df])
        old_df = new_df
    return new_df


def visualise_annotation_counts(df, filename):
    """
    """    
    # plot
    plt.clf()
    plt.barh(df.iloc[:,0], df.iloc[:,1])
    plt.show()
    
    # save figure
    pic_name = filename + '.png'
    plt.savefig(pic_name)


def combine_results(run_id):
    """
    Given a run identifier collect results for this run. Cocatenate the temporary files created per client and peon
    into a big file. Aggregate the counts of same Annotation identifiers. Write the aggregated dataframes to final 
    result count files and produce visualisations, which are saved to file as well.
    :param:
        run_id: identifier of the run to be processed
    """
    GO_num_pat = r'\S*GO_number\S*.csv'
    GO_des_pat = r'\S*GO_description\S*.csv'
    EC_num_pat = r'\S*EC_number\S*.csv'

    # create lists to collect dataframes from files in
    GO_num_file_list = []
    GO_des_file_list = []
    EC_num_file_list = []

    # create dataframes from files found with regex and append to dataframe lists
    path = file_path + run_id + '/'
    for file in os.listdir(path):
        if GO_num_pat.match(file):
            header = ['GO_number', 'counts']
            path_to_file = path + file
            df = read_csv_to_df(path_to_file, header)
            GO_num_file_list.append(df)
        if GO_des_pat.match(file):
            path_to_file = path + file
            header = ['GO_description', 'counts']
            df = read_csv_to_df(path_to_file, header)
            GO_des_file_list.append(df)
        if EC_num_pat.match(file):
            header = ['GO_number', 'counts']
            path_to_file = path + file
            df = read_csv_to_df(path_to_file, header)
            EC_num_file_list.append(df)
    
    # concatenate all files into one dataframe per result type
    header = ['GO_number', 'counts']
    GO_num_new_df = concat_df(header = header, file_list = GO_num_file_list)
    header = ['GO_description', 'counts']
    GO_des_new_df = concat_df(header = header, file_list = GO_des_file_list)
    header = ['EC_number', 'counts']
    EC_num_new_df = concat_df(header = header, file_list = EC_num_file_list)
    
    # aggregate concatenated dataframes to final dataframes
    final_GO_num_df = GO_num_new_df.groupby('GO_number').sum().reset_index()
    final_GO_des_df = GO_des_new_df.groupby('GO_description').sum().reset_index()
    final_EC_num_df = EC_num_new_df.groupby('EC_number').sum.reset_index()

    # create file name without extension
    GO_num_file_name = f'{file_path}{run_id}_final_GO_number_counts'
    GO_des_file_name = f'{file_path}{run_id}_final_GO_description_counts'
    EC_num_file_name = f'{file_path}{run_id}_final_EC_number_counts'

    # write  final dataframes to csv file and produce barplots
    final_GO_num_df.to_csv(f'{GO_num_file_name}.csv', index = False)
    final_GO_des_df.to_csv(f'{GO_des_file_name}.csv', index = False)
    final_EC_num_df.to_csv(f'{EC_num_file_name}.csv', index = False)

    #visualise final dataframes and save the visualisations
    visualise_annotation_counts(df = final_GO_num_df, filename = GO_num_file_name)
    visualise_annotation_counts(df = final_GO_des_df, filename = GO_des_file_name)
    visualise_annotation_counts(df = final_EC_num_df, filename = EC_num_file_name)


if __name__ == '__main__':
    run_ids = ['run_1', 'run_2']
    for run_id in run_ids:
        combine_results(run_id)
