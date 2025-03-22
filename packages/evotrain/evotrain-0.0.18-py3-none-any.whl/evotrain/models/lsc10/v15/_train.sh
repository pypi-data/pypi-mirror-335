#!/bin/bash

# This script is used to submit a job to the cluster
# It takes two arguments: the train script and the config file
# It then modifies the train.sh script to use the config file as job name
# and submits the job to the cluster
# Example: bash _train.sh train_80m.py v0_80m_nodem.json


# Ensure we have the required arguments
if [ $# -lt 1 ]; then
    echo "Usage: bash _train.sh <train_script.py> <config_file.json>"
    exit 1
fi

# Extract job name from the config file (removing the .json extension)
job_name=$(basename "$2" .json)
job_name="${job_name: -4}"

# Modify the train.sh script (use 'sed' for in-place editing)
sed -i "s/#SBATCH --job-name=lsc/#SBATCH --job-name=$job_name/" _train_template.sh

# Call the modified train.sh script
echo "sbatch _train_template.sh $1 $2"
sbatch _train_template.sh $1 $2

# Optionally: Restore the original job name in train.sh after execution
sed -i "s/#SBATCH --job-name=$job_name/#SBATCH --job-name=lsc/" _train_template.sh 
