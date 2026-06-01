#!/bin/bash
#SBATCH -J Au_bulk
#SBATCH -o Au.%j.out
#SBATCH -e Au.%j.err
#SBATCH -p basic
#SBATCH -N 1
#SBATCH -n 4

cd $SLURM_SUBMIT_DIR


mpirun --mca plm isolated \
       --mca btl ^openib \
       -np $SLURM_NTASKS \
       siesta < RUN.fdf > RUN.out
