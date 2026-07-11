#!/bin/bash
# [노드 전용] Hubbard U SCF — QE v6.5(컨테이너)용 구 문법 lda_plus_u 사용
# 마스터(v7.5)에서는 run_scf.sh(신 HUBBARD 카드)를 쓰세요.
set -euo pipefail
QE_MPIRUN="${QE_MPIRUN:-}"        # slurm이 'mpirun -np N' 주입
NPOOL="${NPOOL:-1}"                # k-point pool 병렬 수 (slurm에서 지정)

export OMPI_MCA_pml=ob1
export OMPI_MCA_btl=self,tcp,vader

QE_BIN=pw.x
BASE_INPUT="scf.in"
U_VALUES=("0.0" "1.5" "3.0" "4.5")
OUTDIRS=("../tmp2/" "../tmp3/" "../tmp4/" "../tmp5/")

for idx in "${!U_VALUES[@]}"; do
    U_VALUE="${U_VALUES[$idx]}"
    OUTDIR="${OUTDIRS[$idx]}"
    TAG="U${U_VALUE}"
    INPUT_FILE="scf_${TAG}.in"
    OUTPUT_FILE="scf_${TAG}.out"
    mkdir -p "${OUTDIR}"

    # 구 문법: &system 안에 lda_plus_u + Hubbard_U(1) [Mo=1번째 원자종]
    #  - 기존 HUBBARD 카드(신 문법)는 제거
    #  - outdir 교체
    awk -v outdir="${OUTDIR}" -v uval="${U_VALUE}" '
        BEGIN { in_system=0; skip_hub=0 }
        /^[[:space:]]*outdir[[:space:]]*=/ { print "    outdir = '\''" outdir "'\''"; next }
        /^[[:space:]]*&system/ { in_system=1; print; next }
        # &system 닫히기 직전에 U 설정 삽입 (U=0이면 lda_plus_u 안 넣음)
        in_system && /^[[:space:]]*\// {
            if (uval+0 > 0) {
                print "    lda_plus_u = .true."
                print "    Hubbard_U(1) = " uval
                print "    U_projection_type = '\''ortho-atomic'\''"
            }
            in_system=0; print; next
        }
        # 신 문법 HUBBARD 카드 블록 제거
        /^HUBBARD([[:space:]]|\()/ { skip_hub=1; next }
        skip_hub && /^[[:space:]]*(U|J0|J|V|ALPHA)[[:space:]]+/ { next }
        skip_hub { skip_hub=0 }
        { print }
    ' "${BASE_INPUT}" > "${INPUT_FILE}"

    echo "[U=${U_VALUE}] SCF (npool=${NPOOL}) -> ${OUTDIR}"
    $QE_MPIRUN ${QE_BIN} -npool ${NPOOL} < "${INPUT_FILE}" > "${OUTPUT_FILE}"

    # U가 실제로 먹었는지 검증 (v6.5에서 무시되면 경고)
    if [ "${U_VALUE}" != "0.0" ] && grep -qi "ignored" "${OUTPUT_FILE}"; then
        echo "  [경고] U 카드가 무시됨 — 이 QE 버전이 문법을 지원하는지 확인 필요"
    fi
    echo "  Done: ${OUTPUT_FILE}"
done
echo "All node SCF finished."
