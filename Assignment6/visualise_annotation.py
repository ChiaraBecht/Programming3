import csv
import matplotlib.pyplot as plt
import os
import ReadConfig
import pickle
import pandas as pd

config = ReadConfig.get_config()
file_path = config['storage_location']

def visualise_annotation_counts(file):
    """
    """
    # open file
    with open(file, 'rb') as f:
        GO_num_dict = pickle.load(f)
    
    # plot
    plt.clf()
    plt.barh(list(GO_num_dict.keys()),list(GO_num_dict.values()))
    plt.show()
    
    # save figure
    prefix = file.split('.')[0]
    pic_name = prefix + '.png'
    plt.savefig(pic_name)

    # write dictionary to csv
    csv_name = prefix + '.csv'
    w = csv.writer(open(csv_name, "w"))
    # loop over dictionary keys and values
    for key, val in GO_num_dict.items():
        # write every key and value to file
        w.writerow([key, val])


def visualise_mapping_annotation_status(Mapping_status_file, Annotation_status_file):
    """
    """
    # open Mapping status file
    with open(Mapping_status_file, 'rb') as f:
        Mapping_status_dict = pickle.load(f)

    # open Mapping status file
    with open(Annotation_status_file, 'rb') as f:
        Annotation_status_dict = pickle.load(f)

    # calculate mapping stats
    mapped = Mapping_status_dict['mapped']
    unmapped = Mapping_status_dict['unmapped']
    total = mapped + unmapped
    mapping_stats = {'mapped_count': mapped,
                        'unmapped_count': unmapped,
                        'perc_mapped': mapped / total * 100,
                        'perc_unmapped': unmapped / total * 100}
    
    mapping_stats_df = pd.DataFrame(mapping_stats, index=[0])

    # calculate annotation stats
    annotated = Annotation_status_dict['annotation']
    not_annotated = Annotation_status_dict['no annotation']
    annotated_perc = annotated / mapped * 100
    not_annotated_perc = not_annotated / mapped * 100
    annotation_stats = {'annotated': annotated,
                        'not_annotated': not_annotated,
                        'annotated_perc': annotated_perc,
                        'not_annotated_perc': not_annotated_perc}
    
    annotation_stats_df = pd.DataFrame(annotation_stats, index=[0])

    # defien output folder and file
    map_prefix = Mapping_status_file.split('.')[0]
    map_name = map_prefix + '.csv'
    mapping_stats_df.to_csv(map_name, index = False)

    anot_prefix = Annotation_status_file.split('.')[0]
    anot_name = anot_prefix + '.csv'
    annotation_stats_df.to_csv(anot_name, index = False)
 

def produce_visualisation_stats(run_id):
    """
    """
    path = file_path + run_id + '/'
    # list the files to plot
    plot_file_list = []
    for file in os.listdir(path):
        if file.endswith("count.pkl"):
            path_to_file = path + file
            plot_file_list.append(path_to_file)

    for file in plot_file_list:
        visualise_annotation_counts(file)
    
    # get files to calculate stats
    Annotation_file_list = []
    Mapping_status_file = ""
    for file in os.listdir(path):
        if file.endswith("Annotation_status.pkl"):
            path_to_file = path + file
            Annotation_file_list.append(path_to_file)
        if file.endswith("Mapping_status.pkl"):
            path_to_file = path + file
            Mapping_status_file = path_to_file

    for file in Annotation_file_list:
        visualise_mapping_annotation_status(Mapping_status_file, file)

if __name__ == '__main__':
    visualise_mapping_annotation_status(Mapping_status_file = 'output/Mapping_status.pkl', Annotation_status_file = 'output/GO_Annotation_status.pkl')
