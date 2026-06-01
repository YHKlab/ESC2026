#!/usr/bin/env bash
# SIESTA 5.4.2 — molecular calculation
set -euo pipefail

LABEL="CH4"
WORKDIR="$(pwd)"

mpirun -np "${NCORES}" "${SIESTA_BIN}" RUN.fdf | tee "${LABEL}.out"

echo
echo "[done] 결과 파일: ${LABEL}.out, ${LABEL}.XV, ${LABEL}.ANI, ${LABEL}.RHO, ${LABEL}.MDE"
