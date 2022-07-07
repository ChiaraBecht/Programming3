#!/bin/bash

# run for two hours
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
minimap2 -ax map-ont -t 15 ${reference} ${reads} > /students/2021-2022/master/Chiara_DSLS/Assignment6/output/alignment.sam