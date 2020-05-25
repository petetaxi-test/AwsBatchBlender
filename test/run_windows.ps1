# Assumes the environment variables AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY have been set
# You should also edit the source and destination buckets to match your stack

docker run -it --rm `
   -e AWS_ACCESS_KEY_ID=$Env:AWS_ACCESS_KEY_ID `
   -e AWS_SECRET_ACCESS_KEY=$Env:AWS_SECRET_ACCESS_KEY `
   -e RENDER_SOURCE_BUCKET=fast-render-6-renderblendbucket-1022vic6ux2pp `
   -e RENDER_DEST_BUCKET=fast-render-6-renderresultsbucket-1gfiu6mk4ovpg `
   petebeat/blender:dev0.10 `
   -b d55650d599927f71 -S "CampFire" -x 1920 -y 1080 -s 64 -p 25 -f 140 -e 140 -t 1


