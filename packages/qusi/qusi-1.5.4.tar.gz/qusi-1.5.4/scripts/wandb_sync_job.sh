#!/bin/bash

#SBATCH --job-name="wandb_sync"
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4000
#SBATCH --time=0-00:10:00

cd sessions
srun wandb sync --sync-all
