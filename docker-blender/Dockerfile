FROM petebeat/blenderbase:2.93

LABEL authors="Peter Reay (peterareay@hotmail.com)"

# Blender scripts for configuring and rendering
ADD ./scripts/* /root/scripts/

# Invoke Blender. The 'command' arguments are passed through
# to this script when docker is invoked
ENTRYPOINT ["/bin/bash", "/root/scripts/process_job.sh"]
