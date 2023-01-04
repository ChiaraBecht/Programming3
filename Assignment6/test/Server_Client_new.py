import multiprocessing as mp
from multiprocessing.managers import BaseManager, SyncManager
import time, queue
import argparse as ap
from functools import partial
from Bio import Entrez
from Bio import SeqIO
from collections import defaultdict
import re
import os
import pandas as pd
import sys
from visualise_annotation import produce_visualisation
from process_line import read_process_line
from query_ncbi import query_ncbi
from extract_Annotation_from_gb import extract_GO_EC_numbers

def make_server_manager(port, authkey):
    """ Create a manager for the server, listening on the given port.
        Return a manager object with get_job_q and get_result_q methods.
    """
    job_q = queue.Queue()
    result_q = queue.Queue()

    # This is based on the examples in the official docs of multiprocessing.
    # get_{job|result}_q return synchronized proxies for the actual Queue
    # objects.
    class QueueManager(BaseManager):
        pass

    QueueManager.register('get_job_q', callable=lambda: job_q)
    QueueManager.register('get_result_q', callable=lambda: result_q)

    manager = QueueManager(address=('', port), authkey=authkey)
    manager.start()
    print('Server started at port %s' % port)
    return manager

def runserver(fn, data):
# Start a shared manager server and access its queues
    manager = make_server_manager(PORTNUM, b'whathasitgotinitspocketsesss?')
    shared_job_q = manager.get_job_q()
    shared_result_q = manager.get_result_q()

    if not data:
        print("Gimme something to do here!")
        return
    

    print("Sending data!")
    for d in data:
        print('iterate over data and print each item', d)
        shared_job_q.put({'fn' : fn, 'arg' : d})
        print({'fn' : fn, 'arg' : d})

    time.sleep(2)  

    results = []
    while True:
        try:
            result = shared_result_q.get_nowait()
            results.append(result)
            print("Got result!", result)
            if len(results) == len(data):
                print("Got all results!")
                break
        except queue.Empty:
            time.sleep(1)
            continue
    
    # Tell the client process no more data will be forthcoming
    print("Time to kill some peons!")
    shared_job_q.put(POISONPILL)
    # Sleep a bit before shutting down the server - to give clients time to
    # realize the job queue is empty and exit in an orderly way.
    time.sleep(5)
    print("Aaaaaand we're done for the server!")
    manager.shutdown()
    
    # manage results
    GO_numbers = defaultdict(int)
    GO_nums = []
    GO_n_count = []
    GO_terms = defaultdict(int)
    GO_terms_list = []
    GO_terms_count = []
    EC_numbers = defaultdict(int)
    EC_num_list = []
    EC_counts = []

    for res in results:
        if res['result'] != 'DOH':
            GO_num_dict = res['result'][0]
            GO_des_dict = res['result'][1]
            EC_dict = res['result'][2]

            # create dictionary that adds counts found for each key
            for GO_num in GO_num_dict.keys():
                GO_numbers[GO_num] += GO_num_dict[GO_num]

            for GO_des in GO_des_dict.keys():
                GO_terms[GO_des] += GO_des_dict[GO_des]
            
            
            for EC_num in EC_dict.keys():
                EC_numbers[EC_num] += EC_dict[EC_num]
            
    
    # from the dictionary with identifier as key and count as value make two lists with identifiers and counts
    for GO_n, count in GO_numbers.items():
        GO_nums.append(GO_n)
        GO_n_count.append(count)
    
    for GO_t, count in GO_terms.items():
                GO_terms_list.append(GO_t)
                GO_terms_count.append(count)
    
    for EC_n, count in EC_numbers.items():
                EC_num_list.append(EC_n)
                EC_counts.append(count)
    
    GO_numb_df = pd.DataFrame({'GO_numbers': GO_nums, 'counts': GO_n_count})
    GO_terms_df = pd.DataFrame({'GO_terms': GO_terms_list, 'counts': GO_terms_count})
    EC_numb_df = pd.DataFrame({'EC_numbers': EC_num_list, 'counts': EC_counts})

    out_dir = '/students/2021-2022/master/Chiara_DSLS/Assignment6/output/'

    GO_n_out = out_dir + 'GO_number_count.csv'
    GO_t_out = out_dir + 'GO_terms_count.csv'
    EC_n_out = out_dir + 'EC_numbers_count.csv'

    GO_numb_df.to_csv(GO_n_out, index=False)
    GO_terms_df.to_csv(GO_t_out, index=False)
    EC_numb_df.to_csv(EC_n_out, index=False)

    produce_visualisation()


def make_client_manager(ip, port, authkey):
    """ Create a manager for a client. This manager connects to a server on the
        given address and exposes the get_job_q and get_result_q methods for
        accessing the shared queues from the server.
        Return a manager object.
    """
    class ServerQueueManager(BaseManager):
        pass

    ServerQueueManager.register('get_job_q')
    ServerQueueManager.register('get_result_q')

    manager = ServerQueueManager(address=(ip, port), authkey=authkey)
    manager.connect()

    print('Client connected to %s:%s' % (ip, port))
    return manager


def runclient(num_processes):
    manager = make_client_manager(IP, PORTNUM, AUTHKEY)
    job_q = manager.get_job_q()
    result_q = manager.get_result_q()
    run_workers(job_q, result_q, num_processes)
    
def run_workers(job_q, result_q, num_processes):
    processes = []
    for p in range(num_processes):
        temP = mp.Process(target=peon, args=(job_q, result_q))
        processes.append(temP)
        temP.start()
    print("Started %s workers!" % len(processes))
    for temP in processes:
        temP.join()

def peon(job_q, result_q):
    my_name = mp.current_process().name
    while True:
        try:
            job = job_q.get_nowait()
            if job == POISONPILL:
                job_q.put(POISONPILL)
                print("Aaaaaaargh", my_name)
                return
            else:
                try:
                    result = job['fn'](job['arg'])
                    print("Peon %s Workwork on %s!" % (my_name, job['arg']))
                    result_q.put({'job': job, 'result' : result})
                except NameError:
                    print("Peon %s found exception on %s!" % (my_name, job['arg']))
                    result_q.put({'job': job, 'result' : ERROR})

        except queue.Empty:
            print("sleepytime for", my_name)
            time.sleep(1)


def instructions(filename, line_nr):
    """
    the work a peon has to do:
    - read a line from sam file
    - extract gi_number, start_pos, end_pos
    - download genbank file for given gi_number if file is not present yet
    - extract annotationi from genbank file given file, start_pos, end_pos
    """
    gi_id, read_start_pos, read_stop_pos = read_process_line(filename, line_nr)
    

    if gi_id != 0:
        print(gi_id)
        gb_file = '/students/2021-2022/master/Chiara_DSLS/Assignment6/genbank_cache/' + gi_id + '.gb'
        if os.path.isfile(gb_file):
            print('file present do not download')
            GO_num_counts, GO_des_counts, EC_counts = extract_GO_EC_numbers(gb_file, read_start_pos, read_stop_pos)
        else:
            print('file needs to be downloaded')
            query_ncbi(gi_id)
            GO_num_counts, GO_des_counts, EC_counts = extract_GO_EC_numbers(gb_file, read_start_pos, read_stop_pos)
    
    return GO_num_counts, GO_des_counts, EC_counts


if __name__ == '__main__':
    argparser = ap.ArgumentParser(description="test")
    argparser.add_argument("-n", action="store", dest="n", type=int, help="Number of peons per client.")
    group = argparser.add_mutually_exclusive_group()
    group.add_argument('-c', action='store_true', dest="c")
    group.add_argument('-s', action='store_true', dest="s")
    argparser.add_argument("--port", action="store", dest="port", type=int, help="port number")
    argparser.add_argument("--host", action="store", dest="host", type=str, help="host")
    args = argparser.parse_args()
    print(args)
    n = args.n
    POISONPILL = "MEMENTOMORI"
    ERROR = "DOH"
    IP = args.host
    PORTNUM = args.port
    AUTHKEY = b'whathasitgotinitspocketsesss?'

    lines = []
    with open('/students/2021-2022/master/Chiara_DSLS/Assignment6/output/alignment.sam') as file:
        # get file length measured by characters
        for i,line in enumerate(file):
            lines.append(i)
    
    filename = '/students/2021-2022/master/Chiara_DSLS/Assignment6/output/alignment.sam'
    storage_loc = '/students/2021-2022/master/Chiara_DSLS/Assignment6/output'
    func = partial(instructions, filename)
    
    if args.s:
        server = mp.Process(target=runserver, args=(func, lines))
        server.start()
        time.sleep(1)
        server.join()
        
    
    if args.c:
        client = mp.Process(target=runclient, args=(n,))
        client.start()
        client.join()
