#!/bin/bash

# Exit on any error
set -e


# Example rsync usage
REMOTE_USER="krstulich"
REMOTE_HOST="casper.hpc.ucar.edu"
REMOTE_PATH="/glade/derecho/scratch/krstulich/wrfout/"
LOCAL_PATH="/media/kyle/External_ssd/NCAR/data/"


# Sync data
rsync -avz --progress "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}" "$LOCAL_PATH"

