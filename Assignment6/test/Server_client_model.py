import time, queue
import multiprocessing as mp
from multiprocessing.managers import BaseManager
import argparse as ap

def make_server_manager(port, authkey):
    """ Create a manager for the server, listening on the given port.
        Return a manager object with get_job_q and get_result_q methods.
    """
    job_q = queue.Queue()
    result_q = queue.Queue()

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
    i_data = 0
    print(dir(shared_job_q))
    for i, d in enumerate(data):
        print('iterate over data and print each item', d)
        shared_job_q.put({'fn' : fn, 'arg' : d})
        i_data = i

    time.sleep(2)  

    results = []
    while True:
        try:
            result = shared_result_q.get_nowait()
            results.append(result)
            print("Got result!", result)
            if len(results) == i_data:
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
                    print("Peon %s Workwork yields %s!" % (my_name, result))
                    result_q.put({'job': job, 'result' : result})
                except NameError:
                    print("Can't find yer fun Bob!")
                    result_q.put({'job': job, 'result' : ERROR})

        except queue.Empty:
            print("sleepytime for", my_name)
            time.sleep(1)


def open_file(file):
    counter = 3
    with open(file) as myfile:
        head = [next(myfile) for x in range(counter)]
        #print(head)

def process_line(line):
    line = line.split()
    try:
        ref_id = line[2]
        if ref_id != '*':
            gi_id = ref_id.split('|')[1]
            #start_pos = line[3]
            read_seq = line[3].rstrip() # only correct for my dummy file
            read_len = len(read_seq)
            #end_pos = start_pos + read_len
            #return (gi_id, start_pos, end_pos)
            return (gi_id, read_len)
        else:
            return
    except:
        return


if __name__ == '__main__':
    argparser = ap.ArgumentParser(description="Script that downloads authors to number of user provided articles referenced by the given PubMed ID concurrently.")
    argparser.add_argument("-n", action="store", dest="n", type=int, help="Number of peons per client.")
    group = argparser.add_mutually_exclusive_group()
    group.add_argument('-c', action='store_true', dest="c")
    group.add_argument('-s', action='store_true', dest="s")
    argparser.add_argument("--port", action="store", dest="port", type=int, help="port number")
    argparser.add_argument("--host", action="store", dest="host", type=str, help="host")
    args = argparser.parse_args()
    POISONPILL = "MEMENTOMORI"
    ERROR = "DOH"
    IP = args.host
    PORTNUM = args.port
    AUTHKEY = b'whathasitgotinitspocketsesss?'
    n = args.n
    file = open('dummy1.sam')
    if args.s:
        server = mp.Process(target = runserver,args = (process_line, file)) #process_line, file
        server.start()
        time.sleep(1)
        server.join()

    if args.c:
        client = mp.Process(target=runclient, args = (n, ))
        client.start()
        client.join()