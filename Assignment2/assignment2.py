import multiprocessing as mp
from multiprocessing.managers import BaseManager, SyncManager
import time, queue
import Bio.Entrez
import pickle
import argparse as ap
from pathlib import Path

# set output path
cwd = Path(__file__).parent.absolute()
out_dir_p = cwd / 'output'

def output_directory(out_dir_p):
    """
    Create the output directory in the same directory this script is located
    """
    if not(out_dir_p.exists()):
            out_dir_p.mkdir(parents=True, exist_ok=False)


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
    print(results)

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



Bio.Entrez.email = "chiara.becht@web.de"


# download the article references in order to get the data for the job queue
def download_articles_references(pmid):
    """
    For a given pubmed id download the references from NCBI using Bio.Entrez library
    """
    results = Bio.Entrez.read(Bio.Entrez.elink(dbfrom="pubmed",
                                   db="pmc",
                                   LinkName="pubmed_pmc_refs",
                                   id=pmid,
                                   api_key='c4507f85c841d7430a209603112dba418607'))
    references = [f'{link["Id"]}' for link in results[0]["LinkSetDb"][0]["Link"]]
    return references

# instructions for the client
def download_authors(pmid):
    try:
        handle = Bio.Entrez.esummary(db="pubmed", id=pmid)
        record = Bio.Entrez.read(handle)
        info = tuple(record[0]['AuthorList'])
        print(info)
        handle1 = Bio.Entrez.efetch(db="pmc", id=pmid, rettype="XML", retmode="text",
                           api_key='c4507f85c841d7430a209603112dba418607')
    except RuntimeError:
        info == (None)
    
    with open(f'{out_dir_p}/{pmid}.authors.pkl', 'wb') as handle:
        pickle.dump(info, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    with open(f'{out_dir_p}/{pmid}.xml', 'wb') as file:
        file.write(handle1.read())


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
                    print("Can't find yer fun Bob!")
                    result_q.put({'job': job, 'result' : ERROR})

        except queue.Empty:
            print("sleepytime for", my_name)
            time.sleep(1)



if __name__ == '__main__':
    # Create output directory
    output_directory(out_dir_p)

    #assignment2.py -n <number_of_peons_per_client> [-c | -s] --port <portnumber> --host <serverhost> -a <number_of_articles_to_download> STARTING_PUBMED_ID
    argparser = ap.ArgumentParser(description="Script that downloads authors to number of user provided articles referenced by the given PubMed ID concurrently.")
    argparser.add_argument("-a", action="store", dest="a", required=False, type=int, help="Number of references to download concurrently.")
    argparser.add_argument("-n", action="store", dest="n", type=int, help="Number of peons per client.")
    group = argparser.add_mutually_exclusive_group()
    group.add_argument('-c', action='store_true', dest="c")
    group.add_argument('-s', action='store_true', dest="s")
    argparser.add_argument("--port", action="store", dest="port", type=int, help="port number")
    argparser.add_argument("--host", action="store", dest="host", type=str, help="host")
    argparser.add_argument("STARTING_PUBMED_ID", action="store", nargs=1)
    args = argparser.parse_args()
    print(args)
    print("Getting: ", args.STARTING_PUBMED_ID)
    pmid = args.STARTING_PUBMED_ID
    n = args.n
    POISONPILL = "MEMENTOMORI"
    ERROR = "DOH"
    IP = args.host
    PORTNUM = args.port
    AUTHKEY = b'whathasitgotinitspocketsesss?'
    # get reference list as data
    references = download_articles_references(pmid)
    references = references[0:args.a]
    print(references)

    if args.s:
        server = mp.Process(target=runserver, args=(download_authors, references))
        server.start()
        time.sleep(1)
        server.join()
        
    
    if args.c:
        client = mp.Process(target=runclient, args=(n,))
        client.start()
        client.join()