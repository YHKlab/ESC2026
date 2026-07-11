#!/bin/bash
# [실습 2] Band 계산 및 후처리 실행

# --- 조교 세팅: 에러 방지용 환경 변수 ---
export OMPI_MCA_pml=ob1
export OMPI_MCA_btl=self,tcp
export OMP_NUM_THREADS=1
# ----------------------------------------

# 아래 두 줄을 슬래시 없이 프로그램 이름만 들어가도록 수정합니다.
# pw.x/bands.x 없으면 프로젝트 로컬 환경 활성화 (HOME 미사용)
if ! command -v pw.x >/dev/null 2>&1 || ! command -v bands.x >/dev/null 2>&1; then
    _EXE3_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"   # exe3-qe
    [ -f "$_EXE3_ROOT/setup_env.sh" ] && source "$_EXE3_ROOT/setup_env.sh"
fi

QE_BIN=pw.x
BANDS_BIN=bands.x

mkdir -p ../tmp

echo "[1/2] Band structure 계산 실행 중..."
$QE_BIN < bands.in > bands.out

echo "[2/2] bands.x 후처리 실행 중..."
$BANDS_BIN < bands_pp.in > bands_pp.out

echo "완료. python3 plot_bands.py 로 시각화하세요."
