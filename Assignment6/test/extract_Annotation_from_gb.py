from Bio import SeqIO
import re

def extract_GO_EC_numbers(gb_file, read_start, read_stop):
    """
    """
    # read genbank file
    gb_record = SeqIO.read(open(gb_file, 'r'), 'genbank')

    # check whether read length is one than execute exception, else check which features are spanned
    if (read_stop - read_start) == 1:
        print('READ lenght is 1')
        for locs in gb_record.features:
            # extract the first start and last stop position (this should allow handling joins as well)
            loc = str(locs.location).split(':')
            loc_start = loc[0]
            loc_start = int(re.findall("\d+", loc_start)[0])
            loc_end = loc[-1]
            loc_end = int(re.findall("\d+", loc_end)[0])
            
            # find the feature where the start position is fitting in:
            if loc_start <= read_start <= loc_end:
                print(loc_start, read_start, loc_end)
                try:
                    print('GO FUNCTION', locs.qualifiers['GO_function'])
                    GO = locs.qualifiers['GO_function']
                    for annot in GO:
                        GO_anot = annot.split('-')
                        GO_anot_nr = GO_anot[0]
                        GO_annot_des = GO_anot[1]
                        print(GO_anot)
                except:
                    continue

                try:
                    print('EC NUMBER', locs.qualifiers['EC_number'])
                except:
                    continue
    else:
        print('READ length > 1')
        for locs in gb_record.features:
            # extract the first start and last stop position (this should allow handling joins as well)
            loc = str(locs.location).split(':')
            loc_start = loc[0]
            loc_start = int(re.findall("\d+", loc_start)[0])
            loc_end = loc[-1]
            loc_end = int(re.findall("\d+", loc_end)[0])
            # get all features entirely spanned by a read
            if (read_start <= loc_start <= read_stop) & (read_start <= loc_end <= read_stop):
                print('feature is in this read', read_start, loc_start, loc_end, read_stop)
                try:
                    print('GO FUNCTION', locs.qualifiers['GO_function'])
                    GO = locs.qualifiers['GO_function']
                    for annot in GO:
                        GO_anot = annot.split('-')
                        GO_anot_nr = GO_anot[0]
                        GO_annot_des = GO_anot[1]
                        print(GO_anot)
                except:
                    continue

                try:
                    print('EC NUMBER', locs.qualifiers['EC_number'])
                except:
                    continue
            # get the border cases, where the read starts or ends in a feature (incomplete spanning of a feature by the read)
            if (loc_start <= read_start <= loc_end) or (loc_start <= read_stop <= loc_end):
                print('read starts in this feature:', loc_start, read_start, loc_end, 'or read ends in this feature:', loc_start, read_stop, loc_end)
                try:
                    GO = locs.qualifiers['GO_function']
                    print('GO FUNCTION', type(GO), GO.split[0].split(';'))
                    #for annot in GO:
                    #    GO_anot = annot.split('-')
                    #    GO_anot_nr = GO_anot[0]
                    #    GO_annot_des = GO_anot[1]
                    #    print(GO_anot)
                except:
                    continue

                try:
                    print('EC NUMBER', locs.qualifiers['EC_number'])
                except:
                    continue

if __name__ == '__main__':
    file = '/students/2021-2022/master/Chiara_DSLS/Assignment6/genbank_cache/253771435.gb'
    start = 347
    stop = 1755
    dif = stop - start
    print(dif)
    extract_GO_EC_numbers(file, start, stop)
        