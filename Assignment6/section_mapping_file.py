def raster_file(filename, subfilename, target, numb_servers):
    """
    In case several server with associated clients shall be used to process a big mapping file this function
    can be used to section the file into n subfiles.
    :param:
        filename: path and filename of big mapping file that shall be sectioned
        subfilename: fileprefix chosen by user to e.g. provide run identifiers
        target: path to storage location
        numb_servers: number of servers to be used and therefore number of sections the file should be split into 
    """
    file_len = 0
    with open(filename) as file:
        # get file length measured by characters
        for i, _ in enumerate(file):
            file_len = i
    print(file_len, type(file_len))
    starts = [0]
    for n in range(1, numb_servers):
        # find ranges based on characters
        start = int(file_len // ((numb_servers)/n))
        starts.append(start)
    
    stops = []
    stops = starts[1:]
    stops.append(file_len)
    print(starts)
    print(stops)

    # read specific line from file
    with open(filename) as file:
        for i, st in enumerate(starts):
            print(i, st)
            target = open(f'{target}{subfilename}_{i}.sam', 'w')
            print(target)
            for ln in range(starts[i], stops[i]):
                line = file.readline()
                target.write(line)
            target.close()
        


if __name__ == '__main__':
    raster_file('/students/2021-2022/master/Chiara_DSLS/Assignment6/output/alignment_run1.sam', 'subfile_run1', '/students/2021-2022/master/Chiara_DSLS/Assignment6/output/', 4)
    raster_file('/students/2021-2022/master/Chiara_DSLS/Assignment6/output/alignment_run2.sam', 'subfile_run2', '/students/2021-2022/master/Chiara_DSLS/Assignment6/output/', 4)