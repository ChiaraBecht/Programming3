import multiprocessing as mp
from multiprocessing.managers import BaseManager, SyncManager
import time, queue
from io import SEEK_END

def instructions(filename, line_nr, storage_loc):
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

instructions(filename = 'DUMMY.sam', line_nr = 1, storage_loc = './output')
