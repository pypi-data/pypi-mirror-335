#!/bin/bash

#SBATCH --job-name="/100"
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --mem=512000
#SBATCH --time=5-00:00:00
#SBATCH -p gpu
#SBATCH --gpus=a100:1

srun python scripts/train5.py
