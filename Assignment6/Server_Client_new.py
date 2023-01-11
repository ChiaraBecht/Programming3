import multiprocessing as mp
from multiprocessing.managers import BaseManager
import time, queue
import argparse as ap
from functools import partial
from collections import defaultdict
import os
import pickle
import numpy as np
from pathlib import Path 
import ReadConfig
from process_line import read_process_line
from query_ncbi import query_ncbi
from extract_Annotation_from_gb import extract_GO_EC_numbers
from create_write_result_files import create_result_file

config = ReadConfig.get_config()
storage_location = config['storage_location']
gb_cache = config['genbank_cache']

def make_server_manager(port, authkey):
    """ 
    Create manager for the server, that listens at given port
    :param:
	    port: port number choose 2024 or higher
	    authkey: authorization key as string
    :return:
	    manager: server manager object with get_job_q and get_result_q methods
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
    """
    Fills the job queue with instructions and data. Collects results from the result
    queue. Kills peons as soon as all results are collected. Shuts the server down when
    all jobs are done.
    :param:
	    fn: function that instructs the peons
	    data: data the instructions shall be applied on
    """
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

    time.sleep(2)  

    # manage results
    results = np.zeros(len(data), int)
    index = 0

    while True:
        try:
            result = shared_result_q.get_nowait()
            line_nr = result['result']
            results[line_nr] += 1
            index = len(np.where(results == 1)[0])
            print("Got result!", result)
            print(results)
            if index == len(data):
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

    out_dir_p = Path(storage_location) / run_id
    if not(out_dir_p.exists()):
            out_dir_p.mkdir(parents=True, exist_ok=False)
    
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
                    result_q.put({'job': job, 'result' : job['arg']})
                    create_result_file(out_dir_p, server_client_id, 'GO_number', my_name, result[0])
                    create_result_file(out_dir_p, server_client_id, 'GO_description', my_name, result[1])
                    create_result_file(out_dir_p, server_client_id, 'EC_number', my_name, result[2])
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
    GO_num_counts = defaultdict(int)
    GO_des_counts = defaultdict(int)
    EC_counts = defaultdict(int)
    map_status = 'undetermined'

    # not really necessary try exception bloc because of the exception handling in the submodules but stil included due to paranoia:
    try:
        gi_id, read_start_pos, read_stop_pos, map_status = read_process_line(filename, line_nr)
        

        if gi_id != 0:
            gb_file = gb_cache + gi_id + '.gb'
            if os.path.isfile(gb_file):
                print('file present do not download')
                GO_num_counts, GO_des_counts, EC_counts = extract_GO_EC_numbers(gb_file, read_start_pos, read_stop_pos)
                return GO_num_counts, GO_des_counts, EC_counts, line_nr, map_status
            else:
                print('file needs to be downloaded')
                success_marker = query_ncbi(gi_id)
                if success_marker == 'success':
                    GO_num_counts, GO_des_counts, EC_counts = extract_GO_EC_numbers(gb_file, read_start_pos, read_stop_pos)
                    return GO_num_counts, GO_des_counts, EC_counts, line_nr, map_status
                else:
                    return GO_num_counts, GO_des_counts, EC_counts, line_nr, map_status
        else:
            return GO_num_counts, GO_des_counts, EC_counts, line_nr, map_status
    
    except:
        return GO_num_counts, GO_des_counts, EC_counts, line_nr, map_status


if __name__ == '__main__':
    argparser = ap.ArgumentParser(description="test")
    argparser.add_argument("-r", action="store", dest="r", type=str, help="run_identifier")
    argparser.add_argument("-f", action="store", dest="f", type=str, help="mapping file")
    argparser.add_argument("-n", action="store", dest="n", type=int, help="Number of peons per client.")
    group = argparser.add_mutually_exclusive_group()
    group.add_argument('-c', action='store_true', dest="c")
    group.add_argument('-s', action='store_true', dest="s")
    argparser.add_argument('-d', action='store', dest='d', type=str, help='name or identifier of server or client')
    argparser.add_argument("--port", action="store", dest="port", type=int, help="port number")
    argparser.add_argument("--host", action="store", dest="host", type=str, help="host")
    args = argparser.parse_args()
    print(args)
    run_id = args.r
    mapping_file = args.f
    n = args.n
    server_client_id = args.d
    POISONPILL = "MEMENTOMORI"
    ERROR = "DOH"
    IP = args.host
    PORTNUM = args.port
    AUTHKEY = b'whathasitgotinitspocketsesss?'

    lines = []
    with open(mapping_file) as file:
        # get file length measured by characters
        for i,line in enumerate(file):
            lines.append(i)
    
    filename = mapping_file
    func = partial(instructions, mapping_file)
    
    if args.s:
        server = mp.Process(target=runserver, args=(func, lines))
        server.start()
        time.sleep(1)
        server.join()
        
    
    if args.c:
        client = mp.Process(target=runclient, args=(n,))
        client.start()
        client.join()
