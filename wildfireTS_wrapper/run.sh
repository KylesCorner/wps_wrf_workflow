#!/bin/bash

set -euo pipefail

# get date from command line arguments
START_DATE="$1"
CONFIG_PATH="$2"
FIREID="$3"
JOB_TITLE="$4"

# set all the path variables
WORK_DIR="/glade/u/home/krstulich/wps_wrf_workflow"
ENV_PATH="/glade/work/krstulich/conda-envs/wps_wrf"
PYTHON_SCRIPT="$WORK_DIR/setup_wps_wrf.py"
SCRIPT_DIR="$WORK_DIR/scripts"
LOG_DIR="${WORK_DIR}/logs/${FIREID}/"

# load python environment
module load conda
conda activate "$ENV_PATH"
cd "$WORK_DIR"

# setup logging
mkdir -p ${LOG_DIR}
LOGFILE="$LOG_DIR/${START_DATE}.log"

# run the job
echo "Running $JOB_TITLE for fire $FIREID at $START_DATE"
python3 setup_wps_wrf.py -b "$START_DATE" -c "$CONFIG_PATH" > "$LOGFILE" 2>&1

trap 'echo "SIGTERM received!"; exit 1' TERM
wait
