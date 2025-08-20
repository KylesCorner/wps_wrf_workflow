#!/bin/bash

#PBS -N wrf
#PBS -q main@desched1
#PBS -l select=1:ncpus=128:mpiprocs=128
#PBS -l walltime=12:00:00
#PBS -l job_priority=economy
#PBS -j oe
#PBS -A uumm0004

# Use scratch for temporary files to avoid space limits in /tmp
export TMPDIR=/glade/derecho/scratch/$USER/temp
mkdir -p $TMPDIR

ln -s /glade/u/krstulich/opt/WRF-4.6/run/wrf.exe .

module list

touch WRF_BEG
mpiexec -n 128 ./wrf.exe
touch WRF_END

