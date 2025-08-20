#!/bin/bash

#PBS -N ungrib
#PBS -q casper
#PBS -l select=1:ncpus=1:mpiprocs=1
#PBS -l walltime=0:20:00
#PBS -A uumm0004

# Use scratch for temporary files to avoid space limits in /tmp
export TMPDIR=/glade/derecho/scratch/$USER/temp
mkdir -p $TMPDIR

module load openmpi
module list

mpibind ./ungrib.exe
