#!/bin/bash

#SBATCH --job-name="¯new one"
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --mem=60000
#SBATCH --time=0-00:10:00

srun python scripts/dataset.py
