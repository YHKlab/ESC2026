#!/bin/bash
#SBATCH -J SiH_mpi
#SBATCH -o SiH_mpi.%j.out
#SBATCH -e SiH_mpi.%j.err
#SBATCH -p basic
#SBATCH -N 1
#SBATCH -n 4

cd $SLURM_SUBMIT_DIR

source ~/miniconda3/etc/profile.d/conda.sh
conda activate conda542

export PATH=$HOME/siesta-5.4.2-install/bin:$PATH
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH
export OMP_NUM_THREADS=1

INPUT=sih.fdf

echo "===== ENV ====="
hostname
which siesta
which mpirun
echo "SLURM_NTASKS=$SLURM_NTASKS"
echo "INPUT=$INPUT"

echo "===== LDD ====="
ldd $(which siesta)

echo "===== RUN ====="
mpirun -np $SLURM_NTASKS siesta < $INPUT > RUN.out

echo "===== CHECK ====="
tail -30 RUN.out
