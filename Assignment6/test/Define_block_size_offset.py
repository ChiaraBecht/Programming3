from io import SEEK_END

def raster_file(filename, numb_clients, numb_processes):
    with open(filename) as file:
        # get file length measured by characters
        file.seek(0, SEEK_END)
        f_len = file.tell()
        print(f_len)
        # define list with start character positions
        starts = [0]
        for n in range(1, numb_clients):
            # find ranges based on characters
            file.seek((f_len // ((numb_clients)/n)))
            # find start of next line
            file.readline()
            #store offset
            starts.append(file.tell())
    
    # calcualte stops based on start positions
    stops = starts[1:] + [f_len]
    # zip stats and stops together
    start_stop = zip(starts, stops)
    print(f'starts: {starts}', f'stops: {stops}')

    # get start and positions per process started for each client
    starts_per_process = []
    stops_per_process = []
    with open(filename) as inf:
        start_i = 0
        for start, stop in start_stop:
            #print(f'Stops: {stop}')
            inf.seek(stop)

            #inf_len = inf.tell()
            #print(f'inf_len: {inf_len}')

            starts_clients = [start_i]
            for i in range(1, numb_processes):
                # jump to breakpoint
                inf.seek((i * (stop - start) // numb_processes) + start)
                # find start of next full line
                inf.readline()
                # offset
                starts_clients.append(inf.tell())
            stop_clients = starts_clients[1:] + [stop]
            start_i += (stop - start)
            starts_per_process.append(starts_clients)
            stops_per_process.append(stop_clients)
    print(f'start_proc: {starts_per_process}', f'stops proc:{stops_per_process}')
    return starts, stops, starts_per_process, stops_per_process

client_starts, client_stops, process_starts, process_stops = raster_file('DUMMY.sam', numb_clients = 3, numb_processes = 3)

def read_data():
    """
    Provide client with its start and stop position and as well with the starts and stops for the processes.
    :param:
        client_index: number that defines which blocks to choose: don't know yet how to submit that to the client (maybe argparse argument)
        client_start: line number the client needs to read from
        client_stop: line number the client need to stop reading
        process_starts: list of line numbers where processes of the client need to start reading
        process_stops: list of line numbers where process of the client need to stop reading
    """

