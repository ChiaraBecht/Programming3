import linecache
import multiprocessing as mp

class Reader:
    """
    read x lines from a file. The number of lines has to be chosen by the user. The file reading
    starts at defined line, after reading the block the line pointer is updated. When calling the
    function again, the reading start from the line where the pointer was updated to.
    """
    def __init__(self, datasource, stridelength):
        #create a CsvConverter with the first line of
        #that data-source
        self.file = datasource
        self.stride_length = stridelength
        self.counter = 2
        #self.converter = CsvConverter(linecache.getline(self.file, 1))

    def get_lines(self):
        """
        :param:
            datasource: full path to file
            stridelength: block size of lines which shall be read in one function call
        :return:
            lines: list of tuples with the gi number and the read length
        """
        lines = []
        for x in range(self.counter, self.counter + self.stride_length):
            print('entered loop')
            print('counter', self.counter)
            print('line number', x)
            line = linecache.getline(self.file, x)
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
            
        self.counter += self.stride_length
        print(lines)
        return lines



f = Reader('dummy1.sam', 5)
print(50*'--')
f.get_lines()
print(50*'--')
f.get_lines()