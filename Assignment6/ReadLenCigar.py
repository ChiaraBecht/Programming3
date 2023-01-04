import re

def read_len_from_cigar(cigar_string):
    """
    calculate the length of the mapped read. The start position given in the mapping file refers to the
    leftmost position in the cigar string that is not clipped.

    :param:
        cigar_string: cigar string extracted from a mapping file
    :return:
        seq_len: length of clipped read
    """
    cigar = [cigar_string]
    # get rid of clipping
    cigar_no_clip = [re.sub(r'\d+S', '', cig) for cig in cigar]
    # define regex for all numbers
    numbers = '\d+'
    # extract all numbers from the cigar string
    cigar_list = [re.findall(numbers, cig) for cig in cigar_no_clip]
    # convert the list of numbers in string format to ints
    cigar_list = [list(map(int, cig)) for cig in cigar_list]
    # sum the numbers
    seq_len = [sum(cig) for cig in cigar_list][0]

    return seq_len

if __name__ == '__main__':
    seq_len = read_len_from_cigar('2191S9M2D164M1D1M2D2M1D2M2D32M2D10M2I69M1I3M1D21M1I4M1D24M7D2M2D9M9I23M1D53M3D23M1I15M1I44M2D90M4I7M40D31M1I60M1D8M1I23M2I32M2I2M1I17M1D18M1I4M1D4M4D33M2D2M3I3M3D55M1D36M1I19M1D2M1I21M2D2M1I3M1D3M1I13M1D36M2915S')
    print(seq_len)