#!/bin/bash

# run for thirty minutes
#              d-hh:mm:ss
#SBATCH --time 0-00:30:00

#SBATCH --cpus-per-task=16
#SBATCH --job-name=Chiara

#SBATCH --nodes=1
#SBATCH --output=/students/2021-2022/master/Chiara_DSLS/Assignment6/output/alignment.sam

#SBATCH --partition=assemblix

#SBATCH --error=/students/2021-2022/master/Chiara_DSLS/Assignment6/output/error.log

mkdir -p /students/2021-2022/master/Chiara_DSLS/Assignment6/output/

export reference=/data/dataprocessing/MinIONData/all_bacteria.mmi
export reads=/data/dataprocessing/MinIONData/all.fq

#minimap2 -ax map-ont ${reference} ${reads} > /homes/cbecht/programming3/Programming3/Assignment6/output/alignments.sam
minimap2 -ax map-ont -t 15 ${reference} ${reads} > /students/2021-2022/master/Chiara_DSLS/Assignment6/output/alignment_run1.sam

# store tested parameter settings
#cat /students/2021-2022/master/Chiara_DSLS/Assignment6/output/alignment.sam | head -n 1 >> mapping_parameter_settings_history.txt

# count the lines (not sure whether syntax is correct)
#export file_len=cat /students/2021-2022/master/Chiara_DSLS/Assignment6/output/alignment.sam | wc -l

# get the length of lines containing information
#export text_len=${file_len} - 1

# get rid of the header line, from the rest extract the read identifier and the reference id it was mapped to
#cat /students/2021-2022/master/Chiara_DSLS/Assignment6/output/alignment.sam | tail -n ${text_len} | cut -f 1,3 > /students/2021-2022/master/Chiara_DSLS/Assignment6/output/mapping_summary.csv