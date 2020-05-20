docker run -it --rm `
   -e AWS_ACCESS_KEY_ID=$Env:AWS_ACCESS_KEY_ID `
   -e AWS_SECRET_ACCESS_KEY=$Env:AWS_SECRET_ACCESS_KEY `
   -e RENDER_SOURCE_BUCKET=petebeatrender `
   -e RENDER_DEST_BUCKET=petebeatrenderresults `
   petebeat/blender -x 1080 -y 1080 -b 123 -f 1 -e 1 -s 16 -t 1 -S Scene -p 50


