import multiprocessing as mp
from multiprocessing.managers import BaseManager, SyncManager
import time, queue
import argparse as ap
from functools import partial
from Bio import Entrez
from Bio import SeqIO
from collections import defaultdict

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


def extract_GO_EC_numbers(gb_file, read_start, read_stop):
    """
    """
    # read genbank file
    gb_record = SeqIO.read(open(gb_file, 'r'), 'genbank')

    # dictionary for GO numbers
    GO_num_counts = defaultdict(int)
    # dictionary for GO descriptions
    GO_des_counts = defaultdict(int)
    # dictioanry for EC numbers
    EC_counts = defaultdict(int)

    # check whether read length is one than execute exception, else check which features are spanned
    if (read_stop - read_start) == 1:
        print('READ lenght is 1')
        for locs in gb_record.features:
            # extract the first start and last stop position (this should allow handling joins as well)
            loc = str(locs.location).split(':')
            loc_start = loc[0]
            loc_start = int(re.findall("\d+", loc_start)[0])
            loc_end = loc[-1]
            loc_end = int(re.findall("\d+", loc_end)[0])
            
            # find the feature where the start position is fitting in:
            if loc_start <= read_start <= loc_end:
                print(loc_start, read_start, loc_end)
                try:
                    print('GO FUNCTION COMPLETE', locs.qualifiers['GO_function'])
                    GO = locs.qualifiers['GO_function'][0].split(';')
                    print('GO FUNCTION', GO)
                    for annot in GO:
                        GO_anot = annot.split(' - ')
                        GO_anot_nr = GO_anot[0].lstrip()
                        GO_anot_des = GO_anot[1]
                        print(GO_anot_nr, GO_anot_des)

                        GO_num_counts[GO_anot_nr] += 1
                        GO_des_counts[GO_anot_des] += 1
                except:
                    continue

                try:
                    EC_num = locs.qualifiers['EC_number'][0]
                    print(EC_num)
                    EC_counts[EC_num] += 1
                except:
                    continue
    else:
        print('READ length > 1')
        for locs in gb_record.features:
            # extract the first start and last stop position (this should allow handling joins as well)
            loc = str(locs.location).split(':')
            loc_start = loc[0]
            loc_start = int(re.findall("\d+", loc_start)[0])
            loc_end = loc[-1]
            loc_end = int(re.findall("\d+", loc_end)[0])
            # get all features entirely spanned by a read
            if (read_start <= loc_start <= read_stop) & (read_start <= loc_end <= read_stop):
                print('feature is in this read', read_start, loc_start, loc_end, read_stop)
                try:
                    print('GO FUNCTION COMPLETE', locs.qualifiers['GO_function'])
                    GO = locs.qualifiers['GO_function'][0].split(';')
                    print('GO FUNCTION', GO)
                    for annot in GO:
                        GO_anot = annot.split(' - ')
                        GO_anot_nr = GO_anot[0].lstrip()
                        GO_anot_des = GO_anot[1]
                        print(GO_anot_nr, GO_anot_des)

                        GO_num_counts[GO_anot_nr] += 1
                        GO_des_counts[GO_anot_des] += 1
                except:
                    continue

                try:
                    EC_num = locs.qualifiers['EC_number'][0]
                    print(EC_num)
                    EC_counts[EC_num] += 1
                except:
                    continue
            # get the border cases, where the read starts or ends in a feature (incomplete spanning of a feature by the read)
            if (loc_start <= read_start <= loc_end) or (loc_start <= read_stop <= loc_end):
                print('read starts in this feature:', loc_start, read_start, loc_end, 'or read ends in this feature:', loc_start, read_stop, loc_end)
                try:
                    print('GO FUNCTION COMPLETE', locs.qualifiers['GO_function'])
                    GO = locs.qualifiers['GO_function'][0].split(';')
                    print('GO FUNCTION', GO)
                    for annot in GO:
                        GO_anot = annot.split(' - ')
                        GO_anot_nr = GO_anot[0].lstrip()
                        GO_anot_des = GO_anot[1]
                        print(GO_anot_nr, GO_anot_des)

                        GO_num_counts[GO_anot_nr] += 1
                        GO_des_counts[GO_anot_des] += 1
                except:
                    continue

                try:
                    EC_num = locs.qualifiers['EC_number'][0]
                    print(EC_num)
                    EC_counts[EC_num] += 1
                except:
                    continue
    
    print(GO_num_counts)
    print(GO_des_counts)
    print(EC_counts)

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
