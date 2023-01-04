import pandas as pd
import matplotlib.pyplot as plt
import os
import ReadConfig
import pickle

config = ReadConfig.get_config()
file_path = config['storage_location']

def visualise_output(file):
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
    name = prefix + '.png'
    plt.savefig(name)

def produce_visualisation():
    """
    """
    # list the files
    file_list = []
    for file in os.listdir(file_path):
        if file.endswith(".pkl"):
            path_to_file = file_path + file
            file_list.append(path_to_file)

    for file in file_list:
        visualise_output(file)

if __name__ == '__main__':
    produce_visualisation()