#!/bin/bash

#SBATCH --job-name="infer_job"
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=60000
#SBATCH --time=5-00:00:00
#SBATCH -o "%x.log"

srun python scripts/infer.py
