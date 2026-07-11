#!/bin/bash
# [실습 1] SCF 계산 실행

# --- 조교 세팅: 에러 방지용 환경 변수 ---
export OMPI_MCA_pml=ob1
export OMPI_MCA_btl=self,tcp
export OMP_NUM_THREADS=1
# ----------------------------------------

# pw.x 없으면 프로젝트 로컬 환경 활성화 (HOME 미사용)
if ! command -v pw.x >/dev/null 2>&1; then
    _EXE3_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"   # exe3-qe
    [ -f "$_EXE3_ROOT/setup_env.sh" ] && source "$_EXE3_ROOT/setup_env.sh"
fi

QE_BIN=pw.x

mkdir -p ../tmp

echo "SCF 계산 실행 중..."
$QE_BIN < scf.in > scf.out
