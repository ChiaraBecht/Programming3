#!/bin/bash

# run for 30 minutes
#              d-hh:mm:ss
#SBATCH --time 0-00:30:00

#SBATCH --cpus-per-task=16
#SBATCH --job-name=Chiara

#SBATCH --nodes=1
#SBATCH --output=/students/2021-2022/master/Chiara_DSLS/Assignment6/output/alignment.sam

#SBATCH --partition=assemblix

#SBATCH --error=/students/2021-2022/master/Chiara_DSLS/Assignment6/output/error.log

#mkdir -p /students/2021-2022/master/Chiara_DSLS/Assignment6/output/

export reference=/data/dataprocessing/MinIONData/all_bacteria.mmi
export reads=/data/dataprocessing/MinIONData/all.fq

#minimap2 -ax map-ont ${reference} ${reads} > /homes/cbecht/programming3/Programming3/Assignment6/output/alignments.sam
minimap2 -ax map-ont -t 15 ${reference} ${reads} > /students/2021-2022/master/Chiara_DSLS/Assignment6/output/alignment_run1_1.sam
minimap2 -ax map-ont -t 15 -k 12 -B 2 ${reference} ${reads} > /students/2021-2022/master/Chiara_DSLS/Assignment6/output/alignment_run2.sam

# store tested parameter settings
cat /students/2021-2022/master/Chiara_DSLS/Assignment6/output/alignment_run1.sam | head -n 1 >> /students/2021-2022/master/Chiara_DSLS/Assignment6/output/mapping_parameter_settings_history.txt
cat /students/2021-2022/master/Chiara_DSLS/Assignment6/output/alignment_run2.sam | head -n 1 >> /students/2021-2022/master/Chiara_DSLS/Assignment6/output/mapping_parameter_settings_history.txt