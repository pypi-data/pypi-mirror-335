#!/bin/bash

# yk_train.sh
# Submit a job to the cluster

# Exit immediately if a command exits with a non-zero status
set -e

# Ensure we have the required arguments
if [ $# -lt 2 ]; then
  echo "Usage: bash job_submit.sh <train_script.py> <config_file.json>"
  exit 1
fi

# Extract job parameters from the config file using jq
job_name=$(jq -r '.meta_config.pt_model_name' "$2")
node_name=$(jq -r '.meta_config.node_name' "$2")
email=$(jq -r '.meta_config.email' "$2")
gpus=$(jq -r '.meta_config.gpus' "$2")
memory=$(jq -r '.meta_config.memory' "$2")
cpus_per_task=$(jq -r '.meta_config.cpus_per_task' "$2")
ntasks=$(jq -r '.meta_config.ntasks' "$2")
walltime=$(jq -r '.meta_config.walltime' "$2")

# Create a temporary script with the modified job parameters
tmp_script=$(mktemp)
cat > "$tmp_script" <<EOF
#!/bin/bash
#SBATCH --partition=batch
#SBATCH --job-name=$job_name
#SBATCH --ntasks=$ntasks
#SBATCH --cpus-per-task=$cpus_per_task
#SBATCH --time=$walltime
#SBATCH --mem=$memory
#SBATCH --gpus=$gpus
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=$email
#SBATCH --nodelist=$node_name

source activate eo
srun python "$1"
EOF

# Print the contents of the temporary script
echo "Contents of the temporary script:"
cat "$tmp_script"

# Submit the job
echo "sbatch $tmp_script $1 $2"
sbatch "$tmp_script" "$1" "$2"

# Clean up
rm "$tmp_script"