import pandas as pd
import matplotlib.pyplot as plt
import os

def visualise_output(file):
    """
    """
    plt.clf()
    df = pd.read_csv(file)
    plt.barh(df.iloc[:, 0], df.iloc[:, 1])
    plt.show()
    out_name = file + '.png'
    plt.savefig(out_name)

def produce_visualisation():
    """
    """
    # define path of extracted annotation count files
    path = '/students/2021-2022/master/Chiara_DSLS/Assignment6/output/'

    # list the files
    file_list = []
    for file in os.listdir(path):
        if file.endswith(".csv"):
            path_to_file = path + file
            file_list.append(path_to_file)

    for file in file_list:
        visualise_output(file)

if __name__ == '__main__':
    produce_visualisation()