#!/bin/bash

# store the paths to files as variables
export paired_NGS_1=/data/dataprocessing/MinIONData/MG5267/MG5267_TGACCA_L008_R1_001_BC24EVACXX.filt.fastq
export paired_NGS_2=/data/dataprocessing/MinIONData/MG5267/MG5267_TGACCA_L008_R2_001_BC24EVACXX.filt.fastq

# make an output directory
output=/students/2021-2022/master/Chiara_DSLS/output/
mkdir -p ${output}

output_folder=${output}Chiara_

# parallelise the task for seveal k-mer sizes
seq 29 2 31 | parallel -j16 "velveth ${output_folder}{} {} -longPaired -fastq -separate ${paired_NGS_1} ${paired_NGS_2} &&  velvetg ${output_folder}{} && cat ${output_folder}{}/contigs.fa | python3 assignment4.py -kmers {} >> /students/2021-2022/master/Chiara_DSLS/output/kmer_settings.csv"

output1=/homes/cbecht/programming3/Programming3/Assignment4/output
mkdir -p ${output1}

python3 best_N50.py

rm -r $output_folder*