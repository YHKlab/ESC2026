#!/bin/bash
# [실습 4] 세 물질 DOS (SCF 먼저 필요)
set -uo pipefail
# 마스터: 빈 값(직렬) / 노드 slurm: mpirun -np N 이 주입됨
QE_MPIRUN="${QE_MPIRUN:-}"
NPOOL="${NPOOL:-1}"        # k-point pool 병렬 (slurm에서 주입)
export OMPI_MCA_pml=ob1; export OMPI_MCA_btl=self,tcp; export OMP_NUM_THREADS=1
# pw.x 없으면 프로젝트 로컬 환경 활성화 (HOME 미사용)
if ! command -v pw.x >/dev/null 2>&1; then
    _EXE3_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"   # exe3-qe
    [ -f "$_EXE3_ROOT/setup_env.sh" ] && source "$_EXE3_ROOT/setup_env.sh"
fi
for MAT in graphene Al Si; do
  if [ ! -d ../tmp_${MAT} ]; then echo "  [경고] ../tmp_${MAT} 없음 → 2_scf를 먼저 실행하세요"; continue; fi
  echo "=== [$MAT] nscf + dos ==="
  $QE_MPIRUN pw.x -npool $NPOOL < ${MAT}.nscf.in > ${MAT}.nscf.out
  $QE_MPIRUN dos.x < ${MAT}.dos.in  > ${MAT}.dos.out
done
echo; echo "비교: python3 plot_compare.py"
