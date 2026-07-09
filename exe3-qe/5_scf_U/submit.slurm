#!/bin/bash
#SBATCH --job-name=qe_scfU
#SBATCH --output=qe_scfU.%j.out
#SBATCH --error=qe_scfU.%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=16        # MPI 프로세스 수 (병렬)
#SBATCH --cpus-per-task=1

# === 병렬 설정 ===
#   ntasks = 전체 MPI 프로세스, NPOOL = k-point 병렬 pool 수
#   조건: ntasks가 NPOOL로 나누어떨어져야 함 (예: 16 / 4 = pool당 4프로세스)
NPOOL=4

STAGEDIR=${SLURM_SUBMIT_DIR:-$PWD}
QEROOT="$(cd "$STAGEDIR/.." && pwd)"
STAGE="$(basename "$STAGEDIR")"

# 컨테이너(QE v6.5) 안에서 노드 전용 스크립트 실행
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
    export QE_MPIRUN='mpirun -np 16'
    export NPOOL=
    bash run_scf_node.sh
  "
