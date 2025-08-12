#!/bin/bash

#PBS -N geogrid
#PBS -q casper
#PBS -l select=1:ncpus=4:mpiprocs=4
#PBS -l walltime=0:30:00
#PBS -A p48500047

module load openmpi
module list

touch GEOGRID_BEG
mpibind  ./geogrid.exe
touch GEOGRID_END
