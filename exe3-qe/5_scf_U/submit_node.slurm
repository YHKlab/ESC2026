#!/bin/bash
#SBATCH --job-name=qe_scfU_node
#SBATCH --output=qe_scfU_node.%j.out
#SBATCH --error=qe_scfU_node.%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=8           # MPI 프로세스 (병렬 코어 수)
#SBATCH --cpus-per-task=1

STAGEDIR=${SLURM_SUBMIT_DIR:-$PWD}
QEROOT="$(cd "$STAGEDIR/.." && pwd)"
STAGE="$(basename "$STAGEDIR")"

echo "=== Job 시작: $(date) | ntasks=8, npool=4 ==="
SECONDS=0

singularity exec \
  -B "$QEROOT:/work" \
  /singularity/quantum-mobile___1.0.0 \
  bash -lc "
    unset OPAL_PREFIX
    export OMPI_MCA_pml=ob1
    export OMPI_MCA_btl=self,tcp,vader
    export OMPI_MCA_oob=^ud
    export OMPI_MCA_btl_vader_single_copy_mechanism=none
    cd /work/$STAGE
    export QE_MPIRUN='mpirun -np 8'
    export NPOOL=4
    bash run_scf_node.sh
  "

echo "=== Job 종료: $(date) | 총 소요: ${SECONDS}초 ==="
