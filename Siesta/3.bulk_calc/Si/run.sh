#!/bin/bash
#SBATCH --job-name=Si
#SBATCH --output=Si.slurm.%j.out
#SBATCH --error=Si.slurm.%j.err
#SBATCH --ntasks=4

LABEL="Si"
INPUT="RUN.fdf"
WORKDIR=${SLURM_SUBMIT_DIR:-$PWD}
NTASKS=${SLURM_NTASKS:-4}

cd "$WORKDIR"

export OMPI_MCA_pml=ob1
export OMPI_MCA_btl=tcp,self

rm -f *.DM *.DMHS

/usr/mpi/gcc/openmpi-4.1.5a1/bin/mpirun -np "$NTASKS" \
  singularity exec \
  -B "$WORKDIR:/work" \
  /singularity/siesta_5.4.2.sif \
  bash -lc "cd /work && siesta < $INPUT" > "${LABEL}.out"
