import multiprocessing as mp
from multiprocessing.managers import BaseManager, SyncManager
import time, queue
import argparse as ap
from functools import partial
from Bio import Entrez
from Bio import SeqIO

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

def runserver(fn, data_1): #fn, data
# Start a shared manager server and access its queues
    manager = make_server_manager(PORTNUM, b'whathasitgotinitspocketsesss?')
    shared_job_q = manager.get_job_q()
    shared_result_q = manager.get_result_q()

    if not data_1:
        print("Gimme something to do here!")
        return
    

    print("Sending data!")
    for d in data_1:
        print('iterate over data and print each item', d)
        shared_job_q.put({'fn' : fn, 'arg' : d})
        print({'fn' : fn, 'arg' : d})

    time.sleep(2)  

    results_1 = []
    while True:
        try:
            result = shared_result_q.get_nowait()
            results_1.append(result)
            print("Got result!", result)
            if len(results_1) == len(data_1):
                print("Got all results!")
                break
        except queue.Empty:
            time.sleep(1)
            continue
    
    # results of job 1:
    for res in results_1:
        print(res['result'])
    # Tell the client process no more data will be forthcoming
    print("Time to kill some peons!")
    shared_job_q.put(POISONPILL)
    # Sleep a bit before shutting down the server - to give clients time to
    # realize the job queue is empty and exit in an orderly way.
    time.sleep(5)
    print("Aaaaaand we're done for the server!")
    manager.shutdown()
    #print(results)
    


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
                    result = job['fn'](job['arg']) #result = job['fn'](job['arg'][0], job['arg'][1], job['arg'][2])
                    print("Peon %s Workwork on %s!" % (my_name, job['arg']))
                    result_q.put({'job': job, 'result' : result})
                except NameError:
                    print("Can't find yer fun Bob!")
                    result_q.put({'job': job, 'result' : ERROR})

        except queue.Empty:
            print("sleepytime for", my_name)
            time.sleep(1)


def instructions(filename, storage_loc, line_nr):
    """
    the work a peon has to do:
    - read a line from sam file
    - extract gi_number, start_pos, end_pos
    - download genbank file for given gi_number if file is not present yet
    - extract annotationi from genbank file given file, start_pos, end_pos

    to test the setup:
    - read a line from a file
    - report the content
    - write content to a mass storage
    """
    # read file
    with open(filename) as file:
        for i, line in enumerate(file):
            if i == line_nr:
                print(line)
                l = line
    
    print(l)
    out_file = storage_loc + '/' + str(line_nr) + '.txt'
    f = open(out_file, 'w')
    f.write(l)
    f.close()

def read_process_line(filename, line_nr):
    """
    Open file, read specified line number and extract gi_number and start and stop position
    """
    # read specific line from file
    with open(filename) as file:
        for i, l in enumerate(file):
            if i == line_nr:
                line = l
    
    # process line
    splitted_line = line.split('\t') #should be tab
    print(splitted_line)
    ref_id = splitted_line[2]
    print(ref_id)
    if ref_id != '*':
        gi_id = ref_id.split('|')[1]
        NCBI_id = ref_id.split('|')[3]
        read_seq = splitted_line[9].rstrip()
        start_pos = int(splitted_line[3])
        
        try:
            print('try')
            read_len = len(read_seq)
            stop_pos = int(start_pos) + read_len
            print(gi_id, NCBI_id, start_pos, stop_pos)
            #mapping_info = [gi_id,(start_pos, stop_pos)]
            return gi_id, (start_pos, stop_pos)
        except:
            print('exception: no read sequence')
            read_len = 1
            print(read_len)
            stop_pos = int(start_pos) + read_len
            print(gi_id, NCBI_id, start_pos, stop_pos)
            #mapping_info = [gi_id, (start_pos, stop_pos)]
            return gi_id, (start_pos, stop_pos)
    else:
        return None


def query_nbi(gi_id, out_dir):
    """
    """
    Entrez.email = "chiara.becht@web.de"
    handle = Entrez.efetch(db='nucleotide',
                                id = gi_id, 
                                rettype = 'gbwithparts', 
                                retmode = 'text', 
                                api_key='c4507f85c841d7430a209603112dba418607')
    
    gb_obj = SeqIO.read(handle, 'gb')
    file_name = out_dir + '/' + gi_id + '.gb'
    SeqIO.write(gb_obj, file_name, 'gb')




if __name__ == '__main__':
    argparser = ap.ArgumentParser(description="test")
    #argparser.add_argument("-a", action="store", dest="a", required=False, type=int, help="Number of references to download concurrently.")
    argparser.add_argument("-n", action="store", dest="n", type=int, help="Number of peons per client.")
    group = argparser.add_mutually_exclusive_group()
    group.add_argument('-c', action='store_true', dest="c")
    group.add_argument('-s', action='store_true', dest="s")
    argparser.add_argument("--port", action="store", dest="port", type=int, help="port number")
    argparser.add_argument("--host", action="store", dest="host", type=str, help="host")
    #argparser.add_argument("STARTING_PUBMED_ID", action="store", nargs=1)
    args = argparser.parse_args()
    print(args)
    #print("Getting: ", args.STARTING_PUBMED_ID)
    #pmid = args.STARTING_PUBMED_ID
    n = args.n
    POISONPILL = "MEMENTOMORI"
    ERROR = "DOH"
    IP = args.host
    PORTNUM = args.port
    AUTHKEY = b'whathasitgotinitspocketsesss?'

    lines = []
    with open('Dummy.sam') as file:
        # get file length measured by characters
        for i,line in enumerate(file):
            lines.append(i)
    
    filename = 'Dummy.sam'
    storage_loc = './output'

    data = []
    f_names = []
    s_locs = []
    for line in lines:
        d = [filename, line, storage_loc]
        data.append(d)
        f_names.append(filename)
        s_locs.append(storage_loc)
    
    data_list = [f_names, lines, s_locs]
    #func = partial(instructions, filename, storage_loc)
    func1 = partial(read_process_line, filename)

    # task 2:
    gb_cache = '/students/2021-2022/master/Chiara_DSLS/Assignment6/genbank_cache'
    func2 = partial(query_nbi, gb_cache)
    
    if args.s:
        #server = mp.Process(target=runserver, args=(func, lines))
        server = mp.Process(target=runserver, args=(func1, lines))
        server.start()
        time.sleep(1)
        server.join()
        
    
    if args.c:
        client = mp.Process(target=runclient, args=(n,))
        client.start()
        client.join()
