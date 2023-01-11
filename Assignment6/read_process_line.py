from ReadLenCigar import read_len_from_cigar

def read_process_line(filename, line_nr):
    """
    Open file, read specified line, for this specific read extract gi identifier and the start position.
    Based on either read sequence or cigar string calculate read lenght. In exceptional cases set length to 1.
    From start position and read length calculate the stop position.
    :param:
        filename: mapping file with full path
        line_nr: index of the line that shall be processed
    :return:
        gi_id: gi identifier
        start_pos: start position of read on the reference genome
        stop_pos: stop position of read on the reference genome
        map_indicator: string specifying whether read was mapped or not: 'mapped' | 'unmapped' |'invalid read'
    """
    # read specific line from file
    with open(filename) as file:
        for i, l in enumerate(file):
            if i == line_nr:
                line = l
    
    # indicator whether read was mapped or not
    map_indicator = ''
    try:

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
    except:
        map_indicator = 'invalid read'
        return 0, 0, 0, map_indicator

if __name__ == '__main__':
    for i in range(0, 15):
        print(i)
        result = read_process_line('/students/2021-2022/master/Chiara_DSLS/Assignment6/output/TEST_10.sam', i)
        print(result)
    