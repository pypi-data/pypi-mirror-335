model_name="lcm10-unet-base-v10b"

model_path="/projects/TAP/vegteam/models_dz/lcm10/v1/${model_name}/"
dst_path="/vitodata/vegteam_vol2/models/lcm10/${model_name}"

mkdir -p /vitodata/vegteam_vol2/models/lcm10/

echo $dst_path

umask 002 && rsync -auv zanagad@login.hpc.int.vito.be:${model_path} ${dst_path}
# umask 002 && scp -r zanagad@login.hpc.int.vito.be:${model_path} ${dst_path}