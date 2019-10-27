set -e

AWS_ACCESS_KEY_ID=$(aws --profile default configure get aws_access_key_id)
AWS_SECRET_ACCESS_KEY=$(aws --profile default configure get aws_secret_access_key)

pushd ../docker-blender
docker build -t petebeat/blender .
popd

docker run -it --rm \
   -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
   -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
   -e RENDER_SOURCE_BUCKET=petebeatrender \
   -e RENDER_DEST_BUCKET=petebeatrenderresults \
   petebeat/blender -x 1920 -y 1080 -b 123 -f 1 -e 1 -s 32 -t 1 -S Scene -p 10
