#!/bin/bash

#SBATCH --job-name="improved_infer"
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=7
#SBATCH --mem-per-cpu=4G
#SBATCH --time=5-00:00:00
#SBATCH -p gpu
#SBATCH --gpus=a100_1g.5gb:1

echo "Job shell script started."
srun --unbuffered python -m scripts.infer
