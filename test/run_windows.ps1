# Assumes the environment variables AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY have been set
# You should also edit the source and destination buckets to match your stack

docker run -it --rm `
   -e AWS_ACCESS_KEY_ID=$Env:AWS_ACCESS_KEY_ID `
   -e AWS_SECRET_ACCESS_KEY=$Env:AWS_SECRET_ACCESS_KEY `
   -e RENDER_SOURCE_BUCKET=large-disk-5-renderblendbucket-6638dykhf6yc `
   -e RENDER_DEST_BUCKET=large-disk-5-renderresultsbucket-s86i3cmhuf4s `
   petebeat/blender:dev0.14 `
   -b 8696e49c29c2eef7 -S "MonsterSide" -x 1920 -y 1080 -s 64 -p 25 -f 120 -e 120 -t 1


