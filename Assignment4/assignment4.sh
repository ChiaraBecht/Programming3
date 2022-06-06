#!/bin/bash

# store the paths to files as variables
paired_NGS_1=/data/dataprocessing/MinIONData/MG5267/MG5267_TGACCA_L008_R1_001_BC24EVACXX.filt.fastq
paired_NGS_2=/data/dataprocessing/MinIONData/MG5267/MG5267_TGACCA_L008_R2_001_BC24EVACXX.filt.fastq

# make an output directory
mkdir -p output
output_folder=output/Chiara_

# parallelise the task for seveal k-mer sizes
seq 29 2 31 | parallel -j16 velveth $output_folder{} {} -longPaired -fastq -separate $paired_NGS_1 $paired_NGS_2 

# for now create roadmap  for kmer length 31 (DeBruijn graph)
#velveth ./programming3/Programming3/Assignment4/Chiara 31 -longPaired -fastq -separate /data/dataprocessing/MinIONData/MG5267/MG5267_TGACCA_L008_R1_001_BC24EVACXX.filt.fastq /data/dataprocessing/MinIONData/MG5267/MG5267_TGACCA_L008_R2_001_BC24EVACXX.filt.fastq 

#built contigs
#seq 29 2 31 | parallel -j16 velvetg $output_folder{}

#seq 29 2 31 | parallel -j16 -N5 python3 assignment4.py -kmers {}