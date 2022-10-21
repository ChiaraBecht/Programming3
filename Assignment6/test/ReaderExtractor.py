import linecache
import multiprocessing as mp
import math

def calc_total_lines(datasource):
    """
    calculate the total number of lines in the sam file, that shall be processed.
    :param:
        datasource: the full file path and file name to the sam file
    
    :return:
        total_lines: number of lines in the file
    """
    # open file in read mode
    with open(datasource, 'r') as fp:
        for count, line in enumerate(fp):
            pass
    print('Total Lines', count + 1)
    return count + 1


def get_lines(data_source, stride_length):
    """
    read x lines from a file. The number of lines has to be chosen by the user. The file reading
    starts at defined line, after reading the block the line pointer is updated. When calling the
    function again, the reading start from the line where the pointer was updated to.
    :param:
        datasource: full path to file
        stridelength: block size of lines which shall be read in one function call
    :return:
        lines: list of tuples with the gi number and the read length
    """
    counter = 2
    lines = []
    for x in range(counter, counter + stride_length):
        print('entered loop')
        print('counter', counter)
        print('line number', x)
        line = linecache.getline(data_source, x)
        splitted_line = line.split('    ') #should be tab
        print(splitted_line)
        try:
            ref_id = splitted_line[2]
            if ref_id != '*':
                gi_id = ref_id.split('|')[1]
                read_seq = splitted_line[3].rstrip() # only correct for my dummy file
                read_len = len(read_seq)
                lines.append((gi_id, read_len))
                print(lines)
        except:
            print('exception', x, line)
            break
        
    counter += stride_length
    print(lines)
    return lines

"""
import functools

if __name__ == '__main__':
    cpus = 2
    num_lines = calc_total_lines('dummy1.sam')
    with mp.Pool(cpus) as pool:
        results = pool.map(functools.partial(get_lines, 'dummy1.sam'), range(num_lines))
    #inputs = [('dummy1.sam', 4), ('dummy1.sam', 3)]
    #with mp.Pool(cpus) as pool:
    #    results = pool.starmap(get_lines, inputs)
"""