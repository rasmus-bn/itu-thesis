#!/bin/bash

# Check for one argument
if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <job_id>"
  exit 1
fi

JOB_ID="$1"
REMOTE_USER="jlis"
REMOTE_HOST="hpc.itu.dk"
REMOTE_DIR="/home/jlis/output/job_${JOB_ID}"
LOCAL_DIR="./output/"

# Copy the directory
scp -r "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}" ${LOCAL_DIR}
