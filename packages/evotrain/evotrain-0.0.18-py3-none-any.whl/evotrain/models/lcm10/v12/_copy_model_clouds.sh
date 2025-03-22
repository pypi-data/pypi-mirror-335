
model_name="2412170939_v5lr0002g975"

model_path="/projects/TAP/vegteam/models_clouds/${model_name}/"

dst_path="/vitodata/vegteam_vol2/models/cloudsen/60m/${model_name}"

mkdir -p /vitodata/vegteam_vol2/models/cloudsen/60m/

echo $dst_path

umask 002 && rsync -auv zanagad@login.hpc.int.vito.be:${model_path} ${dst_path}
# umask 002 && scp -r zanagad@login.hpc.int.vito.be:${model_path} ${dst_path}