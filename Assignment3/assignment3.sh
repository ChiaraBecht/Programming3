#!/bin/bash

# run for two hours
#              d-hh:mm:ss
#SBATCH --time=0-02:00:00

#SBATCH --cpus-per-task=16
#SBATCH --job-name=Chiara

#SBATCH --nodes=1

#SBATCH --output=outfile
#SBATCH--partition=assemblix
mkdir -p output

export time_file=output/timings.txt
export time=/usr/bin/time
export BLASTDB=/local-fs/datasets/refseq_protein/refseq_protein
export blastoutput=output/blastoutput.txt

for i in {1..16} ; do $time -a -o $time_file -f ${i}"\t"%e blastp -query MCRA.faa -db $BLASTDB -num_threads $i -outfmt 6 >> $blastoutput; done

python3 assignment3.py
