#!/bin/bash

#SBATCH --job-name="datasetNan"
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=512000
#SBATCH --time=5-00:00:00

# max nodes in 1 cpu
srun python scripts/dataset.py
