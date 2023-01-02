import linecache
def process_line(line):
    """
    Extract the relevant features from the mapping file: reference identifier of the genome, start pos, sequence length. stop position.
    The stop position of the read is given indirectly by adding the sequence length to the start position. In some cases the sequence
    length is not given, then the length is set to 1.
    :params:
        s
    :return:
    
    """
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
            mapping_info = [gi_id,(start_pos, stop_pos)]
            return mapping_info
        except:
            print('exception: no read sequence')
            read_len = 1
            print(read_len)
            stop_pos = int(start_pos) + read_len
            print(gi_id, NCBI_id, start_pos, stop_pos)
            mapping_info = [gi_id, (start_pos, stop_pos)]
            return mapping_info
    else:
        print('exception: no ref id')

if __name__ == '__main__':
    #line = linecache.getline('/students/2021-2022/master/Chiara_DSLS/Assignment6/output/alignment.sam', 2)
    with open('/students/2021-2022/master/Chiara_DSLS/Assignment6/output/alignment.sam', 'r') as file:
        file.readline()
        file.readline()
        line = file.readline()
    result = process_line(line)
    print(result)
    