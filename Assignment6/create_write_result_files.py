import csv

def create_result_file(out_dir, client_id, filename, process, result_dict):
    """
    """
    with open(f'{out_dir}/{client_id}_{filename}_process{process}.csv', 'a') as file:
        writer = csv.writer(file, delimiter = '|')
        for key, value in result_dict.items():
            writer.writerow([key, value])


if __name__ == '__main__':
    my_dictt = {'GO_1': 45435, 'GO_2': 33443}
    create_result_file('/students/2021-2022/master/Chiara_DSLS/Assignment6/Assignment6', 'client1', 'GO_name', 1, my_dictt)
    #create_result_file('/students/2021-2022/master/Chiara_DSLS/Assignment6/Assignment6', 'client1', 'EC_name', 1, dictt)
