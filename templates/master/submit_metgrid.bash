#!/bin/bash

#PBS -N metgrid
#PBS -q casper
#PBS -l select=1:ncpus=16:mpiprocs=16:mem=32GB
#PBS -l walltime=0:20:00
#PBS -A p48500047

# Use scratch for temporary files to avoid space limits in /tmp
export TMPDIR=/glade/derecho/scratch/$USER/temp
mkdir -p $TMPDIR

module load openmpi
module list

touch METGRID_BEG
mpibind ./metgrid.exe
touch METGRID_END
