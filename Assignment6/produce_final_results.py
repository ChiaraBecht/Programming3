import matplotlib.pyplot as plt
import os
import re
import ReadConfig
import pandas as pd
from wordcloud import WordCloud

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
    #headers = header
    df = pd.read_csv(file, delimiter= '|', names = header) # , header = None
    return df


def concat_df(file_list):
    """
    Concatenate all dataframes that belong to one annotation type and run.
    :param:
        file_list: list with all dataframes that belong to an annotation type and run
    :return:
        new_df: concatenated dataframe
    """
    old_df = file_list[0]
    for df in file_list[1:]:
        new_df = pd.concat([old_df, df])
        old_df = new_df
    return new_df

def visualise_most_abundant_terms(GO_des_df, run_id):
    """
    Create a wordcloud of the most abundant terms. No filtering is applied to the terms.
    :param:
        GO_des_df: dataframe with summed counts for each GO description
        run_id: run identifier
    """
    # make wordcloud
    terms = GO_des_df.GO_description.to_list()
    amount = GO_des_df.counts.to_list()
    cleaned_terms = [term.split('[')[0] for term in terms]
    final_terms = []
    for term, count in zip(cleaned_terms, amount):
        t = term * count
        final_terms.append(t)

    final_terms = ''.join(final_terms)

    # Create the wordcloud object
    wordcloud = WordCloud(width=480, height=480, margin=0).generate(final_terms)

    # Display the generated image:
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.margins(x=0, y=0)
    pic_name = file_path + run_id + '_wordcloud.png'
    print(pic_name)
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
        if re.match(GO_num_pat, file):
            header = ['GO_number', 'counts']
            path_to_file = path + file
            df = read_csv_to_df(path_to_file, header)
            GO_num_file_list.append(df)
        if re.match(GO_des_pat, file):
            path_to_file = path + file
            header = ['GO_description', 'counts']
            df = read_csv_to_df(path_to_file, header)
            GO_des_file_list.append(df)
        if re.match(EC_num_pat, file):
            header = ['EC_number', 'counts']
            path_to_file = path + file
            df = read_csv_to_df(path_to_file, header)
            EC_num_file_list.append(df)
    
    # concatenate all files into one dataframe per result type
    GO_num_new_df = concat_df(file_list = GO_num_file_list)
    GO_des_new_df = concat_df(file_list = GO_des_file_list)
    EC_num_new_df = concat_df(file_list = EC_num_file_list)
    
    # aggregate concatenated dataframes to final dataframes
    final_GO_num_df = GO_num_new_df.groupby('GO_number').sum().reset_index()
    final_GO_des_df = GO_des_new_df.groupby('GO_description').sum().reset_index()
    final_EC_num_df = EC_num_new_df.groupby('EC_number').sum().reset_index()
    print('GO_numbers condensed', len(final_GO_num_df.index))
    print('GO_descriptions condensed', len(final_GO_des_df.index))
    print('EC_numbers condensed', len(final_EC_num_df.index))
    print('Total GO number counts', final_GO_num_df.counts.sum())
    print('Total GO description counts', final_GO_des_df.counts.sum())
    print('Total EC number counts', final_EC_num_df.counts.sum())

    # create file name without extension
    GO_num_file_name = f'{file_path}{run_id}_final_GO_number_counts'
    GO_des_file_name = f'{file_path}{run_id}_final_GO_description_counts'
    EC_num_file_name = f'{file_path}{run_id}_final_EC_number_counts'

    # write  final dataframes to csv file and produce barplots
    final_GO_num_df.to_csv(f'{GO_num_file_name}.csv', index = False)
    final_GO_des_df.to_csv(f'{GO_des_file_name}.csv', index = False)
    final_EC_num_df.to_csv(f'{EC_num_file_name}.csv', index = False)
    final_GO_num_df.sort_values(['counts'], ascending=False).head(20).to_csv(f'{GO_num_file_name}_top_20.csv', index = False)
    final_EC_num_df.sort_values(['counts'], ascending=False).head(20).to_csv(f'{EC_num_file_name}_top_20.csv', index = False)

    # visualise the most abundant GO terms
    visualise_most_abundant_terms(final_GO_des_df, run_id)


if __name__ == '__main__':
    run_ids = ['run_1', 'run_2']
    for run_id in run_ids:
        combine_results(run_id)
