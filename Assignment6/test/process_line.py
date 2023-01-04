import linecache
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
    #print(splitted_line)
    ref_id = splitted_line[2]
    #print(ref_id)
    if ref_id != '*':
        gi_id = ref_id.split('|')[1]
        read_seq = splitted_line[9].rstrip()
        start_pos = int(splitted_line[3])
        
        try:
            #print('try')
            read_len = len(read_seq)
            stop_pos = int(start_pos) + read_len
            #print(gi_id, NCBI_id, start_pos, stop_pos)
            #mapping_info = [gi_id,(start_pos, stop_pos)]
            return gi_id, start_pos, stop_pos
        except:
            #print('exception: no read sequence')
            read_len = 1
            #print(read_len)
            stop_pos = int(start_pos) + read_len
            #print(gi_id, NCBI_id, start_pos, stop_pos)
            #mapping_info = [gi_id, (start_pos, stop_pos)]
            return gi_id, start_pos, stop_pos
    else:
        return 0, 0, 0

if __name__ == '__main__':
    #line = linecache.getline('/students/2021-2022/master/Chiara_DSLS/Assignment6/output/alignment.sam', 2)
    with open('/students/2021-2022/master/Chiara_DSLS/Assignment6/output/alignment.sam', 'r') as file:
        file.readline()
        file.readline()
        line = file.readline()
    result = read_process_line(line)
    print(result)
    