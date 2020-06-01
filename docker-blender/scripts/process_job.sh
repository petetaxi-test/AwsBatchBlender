#! /bin/bash
# A bash script, which is a poor man's substitute for the Python version
# but has the considerable advantage that it works

# Abort on errors
set -e

# Process the command line args. It would be nicer to use the longform
# rather than single letter arguments. TODO - work out how to do this.
while getopts "b:s:x:y:p:t:f:e:j:S:" option
do
 case "${option}"
 in
  s) RENDER_SAMPLES=${OPTARG};;
  x) RENDER_XRES=${OPTARG};;
  y) RENDER_YRES=${OPTARG};;
  p) RENDER_PERCENTAGE=${OPTARG};;
  t) RENDER_STEP=${OPTARG};;
  f) RENDER_STARTFRAME=${OPTARG};;
  e) RENDER_ENDFRAME=${OPTARG};;
  b) RENDER_BLEND=${OPTARG};;
  S) RENDER_SCENE=${OPTARG};;
 esac
done

# Mount the working drive to give us extra disk space
mkdir /mnt/workdrive
if [[ `lsblk | grep xvda1` ]]; then
    echo "Device found at /dev/xvda1, mounting work drive"
    mount /dev/xvda1 /mnt/workdrive
else
    echo "No work drive found"
fi
df -ah

# Source and destination file names
SOURCE_OBJECT=Job.${RENDER_BLEND}.zip
DEST_OBJECT="Job.${RENDER_BLEND}-${RENDER_SCENE}-${RENDER_XRES}x${RENDER_YRES}s${RENDER_SAMPLES}p${RENDER_PERCENTAGE}-from${RENDER_STARTFRAME}to${RENDER_ENDFRAME}j${RENDER_STEP}.Results.zip"
DEST_OBJECT="$(echo -e "${DEST_OBJECT}" | tr -d '[:space:]')"

BLENDER=/usr/local/blender/blender
PYTHON_SCRIPT=/root/scripts/do_render.py

UNIQUE_KEY=`cat /proc/sys/kernel/random/uuid`
WORK_DIR=/mnt/workdrive/${UNIQUE_KEY}
mkdir ${WORK_DIR}
echo "Created work dir ${WORK_DIR}"

# Clean up the workdir whether successful or failed
trap 'echo "Deleting work directory"; cd ~; rm -Rf ${WORK_DIR}' EXIT

BLEND_DIR=${WORK_DIR}/blend
SOURCE_LOCAL_ZIP=${BLEND_DIR}/job.zip
OUTPUT_DIR=${WORK_DIR}/render_output

# Get the input ready to render
mkdir ${BLEND_DIR}
aws s3 cp "s3://${RENDER_SOURCE_BUCKET}/${SOURCE_OBJECT}" "${SOURCE_LOCAL_ZIP}"
unzip "${SOURCE_LOCAL_ZIP}" -d "${BLEND_DIR}"

# Pre-render hook script
PRE_RENDER_HOOK=${BLEND_DIR}/pre_render.sh

if [ -f ${PRE_RENDER_HOOK} ]; then
    echo "Executing hook_script pre_render.sh"
    dos2unix ${PRE_RENDER_HOOK}
    CURRENT_DIR=`pwd`
    cd ${BLEND_DIR}
    chmod 755 ./pre_render.sh
    ./pre_render.sh
    cd ${CURRENT_DIR}
    echo "Finished hook_script pre_render.sh"
else
    echo "No pre_render.sh hook was present"
fi

BLEND_FILE=${BLEND_DIR}/job.blend

# Run blender with the appropriate arguments
${BLENDER} -b -noaudio "${BLEND_FILE}" -S "${RENDER_SCENE}" --python ${PYTHON_SCRIPT} -- \
    --samples ${RENDER_SAMPLES} \
    --xres ${RENDER_XRES} \
    --yres ${RENDER_YRES} \
    --percentage ${RENDER_PERCENTAGE} \
    --step ${RENDER_STEP} \
    --startframe ${RENDER_STARTFRAME} \
    --endframe ${RENDER_ENDFRAME} \
    --blend ${UNIQUE_KEY}

# Post render hook script
POST_RENDER_HOOK=${BLEND_DIR}/post_render.sh

if [ -f ${POST_RENDER_HOOK} ]; then
    echo "Executing hook_script post_render.sh"
    dos2unix ${POST_RENDER_HOOK}
    CURRENT_DIR=`pwd`
    cd ${BLEND_DIR}
    chmod 755 ./post_render.sh
    ./post_render.sh
    cd ${CURRENT_DIR}
    echo "Finished hook_script post_render.sh"
else
    echo "No post_render.sh hook was present"
fi

# Push the result to S3
cd ${OUTPUT_DIR}
zip -r "/tmp/${DEST_OBJECT}" .
aws s3 cp "/tmp/${DEST_OBJECT}" "s3://${RENDER_DEST_BUCKET}/${DEST_OBJECT}"

