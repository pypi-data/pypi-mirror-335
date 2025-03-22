#!/bin/bash 

#SBATCH --partition=batch                   # Name of Partition (default is batch)
#SBATCH --job-name=cloudseg                 # Name of job
#SBATCH --ntasks=1                          # Number of CPU processes
#SBATCH --cpus-per-task=10                   # Number of CPU threads
#SBATCH --time=72:00:00                     # Wall time (format: d-hh:mm:ss)
#SBATCH --mem=16gb                          # Amount of memory (units: gb, mg, kb)
#SBATCH --gpus=1                            # Number of GPU
#SBATCH --mail-type=BEGIN,END,FAIL               # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=daniele.zanaga@vito.be           # Where to send email
#SBATCH --nodelist=sasdsnode05

# Load the most recent version of CUDA
module load CUDA

# Activate pre-installed python environment
source activate eo

train_script="$1"
config_path="$2"
# config_path="/projects/TAP/vegteam/models_dz/configs/${model_name}.json"

# Run your python script here (don't forget to use srun)
srun python "$train_script" "$config_path"




