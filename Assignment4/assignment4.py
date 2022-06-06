from Bio import SeqIO
import numpy as np
import argparse as ap

argparser = ap.ArgumentParser(description="Read kmer size")
argparser.add_argument("-kmers", action="store",
                           dest="kmers", required=True, type=int,
                           help="number of kmers used to build this assembly.")
args = argparser.parse_args()
kmer = str(args.kmers)
file_name = 'output/Chiara_{}/contigs.fa'.format(kmer)
records = SeqIO.parse(file_name, 'fasta')

contigs_len = []
for record in records:
    seq = len(record.seq._data.upper())
    contigs_len.append(seq)

#print(contigs_len)

#calculate N50
sorted_contigs_len = sorted(contigs_len)[::-1]
#print(sorted_contigs_len)

cum_sum_contig = np.cumsum(np.array([sorted_contigs_len]))
#print(cum_sum_contig)
half_cum_sum = cum_sum_contig[-1]/2
#print(half_cum_sum)

N50_index = np.searchsorted(cum_sum_contig, half_cum_sum)
N50 = sorted_contigs_len[N50_index]
print(N50)