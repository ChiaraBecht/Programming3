from Bio import SeqIO
import re
from collections import defaultdict

def extract_GO_EC_numbers(gb_file, read_start, read_stop):
    """
    """
    gb_record = SeqIO.read(open(gb_file, 'r'), 'genbank')

    # dictionary for GO numbers
    GO_num_counts = defaultdict(int)
    # dictionary for GO descriptions
    GO_des_counts = defaultdict(int)
    # dictioanry for EC numbers
    EC_counts = defaultdict(int)

    # check whether read length is one than execute exception, else check which features are spanned
    if (read_stop - read_start) == 1:
        for locs in gb_record.features:
            # extract the first start and last stop position (this should allow handling joins as well)
            loc = str(locs.location).split(':')
            loc_start = loc[0]
            loc_start = int(re.findall("\d+", loc_start)[0])
            loc_end = loc[-1]
            loc_end = int(re.findall("\d+", loc_end)[0])
            
            # find the feature where the start position is fitting in:
            if loc_start <= read_start <= loc_end:
                try:
                    GO = locs.qualifiers['GO_function'][0].split(';')
                    for annot in GO:
                        GO_anot = annot.split(' - ')
                        GO_anot_nr = GO_anot[0].lstrip()
                        GO_anot_des = GO_anot[1]

                        GO_num_counts[GO_anot_nr] += 1
                        GO_des_counts[GO_anot_des] += 1
                except:
                    continue

                try:
                    EC_num = locs.qualifiers['EC_number'][0]
                    EC_counts[EC_num] += 1
                except:
                    continue
    else:
        for locs in gb_record.features:
            # extract the first start and last stop position (this should allow handling joins as well)
            loc = str(locs.location).split(':')
            loc_start = loc[0]
            loc_start = int(re.findall("\d+", loc_start)[0])
            loc_end = loc[-1]
            loc_end = int(re.findall("\d+", loc_end)[0])
            # get all features entirely spanned by a read
            if (read_start <= loc_start <= read_stop) & (read_start <= loc_end <= read_stop):
                #print('feature is in this read', read_start, loc_start, loc_end, read_stop)
                try:
                    GO = locs.qualifiers['GO_function'][0].split(';')
                    for annot in GO:
                        GO_anot = annot.split(' - ')
                        GO_anot_nr = GO_anot[0].lstrip()
                        GO_anot_des = GO_anot[1]

                        GO_num_counts[GO_anot_nr] += 1
                        GO_des_counts[GO_anot_des] += 1
                except:
                    continue

                try:
                    EC_num = locs.qualifiers['EC_number'][0]
                    EC_counts[EC_num] += 1
                except:
                    continue
            # get the border cases, where the read starts or ends in a feature (incomplete spanning of a feature by the read)
            if (loc_start <= read_start <= loc_end) or (loc_start <= read_stop <= loc_end):
                try:
                    GO = locs.qualifiers['GO_function'][0].split(';')
                    for annot in GO:
                        GO_anot = annot.split(' - ')
                        GO_anot_nr = GO_anot[0].lstrip()
                        GO_anot_des = GO_anot[1]

                        GO_num_counts[GO_anot_nr] += 1
                        GO_des_counts[GO_anot_des] += 1
                except:
                    continue

                try:
                    EC_num = locs.qualifiers['EC_number'][0]
                    EC_counts[EC_num] += 1
                except:
                    continue
    return GO_num_counts, GO_des_counts, EC_counts

if __name__ == '__main__':
    file = '/students/2021-2022/master/Chiara_DSLS/Assignment6/genbank_cache/253771435.gb'
    start = 1
    stop = 20000
    dif = stop - start
    print(dif)
    extract_GO_EC_numbers(file, start, stop)
        