import numpy as np
import argparse as ap
import sys

# catch kmersize
argparser = ap.ArgumentParser(description="Read kmer size")
argparser.add_argument("-kmers", action="store",
                           dest="kmers", required=True,
                           help="number of kmers used to build this assembly.")
                           
args = argparser.parse_args()
kmer = args.kmers

# define empty list to 
records = []

# read contig file from stdin
output = sys.stdin.readlines()
for line in output:
    if line.startswith('>'):
        start = line.split('N')[0] # splt and strip away the header
        records.append(start) # append > as separator to the record list
    else:
        records.append(line.rstrip('\n')) # append the sequence lines

# make everything a big string and then split it to a list on >
records = ''.join(records)
sequence = records.split('>')
sequence = sequence[1:]

# calculate the length of contigs
contigs_len = []
for record in sequence:
    seq = len(record)
    contigs_len.append(seq)


#sort contigs by length
sorted_contigs_len = sorted(contigs_len)[::-1]

# form cumulative sum
cum_sum_contig = np.cumsum(np.array([sorted_contigs_len]))

#print(cum_sum_contig)

# find median 
half_cum_sum = cum_sum_contig[-1]/2

# find N50 index
N50_index = np.searchsorted(cum_sum_contig, half_cum_sum)

# find N50
N50 = sorted_contigs_len[N50_index]
#print(N50)

sys.stdout.write(f"{kmer},{N50}\n") 