import linecache
from ReadLenCigar import read_len_from_cigar

def read_process_line(filename, line_nr):
    """
    Open file, read specified line number and extract gi_number and start and stop position
    """
    # read specific line from file
    with open(filename) as file:
        for i, l in enumerate(file):
            if i == line_nr:
                line = l
    
    # indicator whether read was mapped or not
    map_indicator = ''
    # process line
    splitted_line = line.split('\t')
    ref_id = splitted_line[2]
    if ref_id != '*':
        map_indicator = 'mapped'
        gi_id = ref_id.split('|')[1]
        read_seq = splitted_line[9].rstrip()
        cigar = splitted_line[5]
        start_pos = int(splitted_line[3])
        
        if read_seq != '*':
            read_len = len(read_seq)
            stop_pos = int(start_pos) + read_len
            return gi_id, start_pos, stop_pos, map_indicator
        
        elif cigar != '*':         
            cigar_len = read_len_from_cigar(cigar)
            stop_pos = int(start_pos) + cigar_len
            return gi_id, start_pos, stop_pos, map_indicator
        
        else:
            read_len = 1
            stop_pos = int(start_pos) + read_len
            return gi_id, start_pos, stop_pos, map_indicator
    else:
        map_indicator = 'unmapped'
        return 0, 0, 0, map_indicator

if __name__ == '__main__':
    result = read_process_line('Dummy.sam', 5)
    print(result)
    