#!/bin/bash


set -euo pipefail

# get date from command line arguments
START_DATE="$1"
CONFIG_PATH="$2"
FIREID="$3"

echo "Running for ${FIREID} ${START_DATE} ${CONFIG_PATH}"
sleep 3
