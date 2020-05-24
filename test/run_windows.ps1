# Assumes the environment variables AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY have been set
# You should also edit the source and destination buckets to match your stack

docker run -it --rm `
   -e AWS_ACCESS_KEY_ID=$Env:AWS_ACCESS_KEY_ID `
   -e AWS_SECRET_ACCESS_KEY=$Env:AWS_SECRET_ACCESS_KEY `
   -e RENDER_SOURCE_BUCKET=fast-render-6-renderblendbucket-1022vic6ux2pp `
   -e RENDER_DEST_BUCKET=fast-render-6-renderresultsbucket-1gfiu6mk4ovpg `
   petebeat/blender:dev0.9 `
   -b d79a00db78843195 -S "Scene" -x 1920 -y 1080 -s 16 -p 25 -f 1 -e 1 -t 1


