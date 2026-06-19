#!/bin/bash
#SBATCH --job-name=NH3
#SBATCH --output=NH3.slurm.%j.out
#SBATCH --error=NH3.slurm.%j.err
#SBATCH --ntasks=4

LABEL="NH3"
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
