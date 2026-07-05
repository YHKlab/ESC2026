#!/bin/bash
# [노드 전용] Hubbard U Band — QE v6.5(컨테이너)용 구 문법
# 마스터(v7.5)에서는 run_bands.sh를 쓰세요. 반드시 run_scf_node.sh 먼저 실행!
set -euo pipefail
QE_MPIRUN="${QE_MPIRUN:-}"
NPOOL="${NPOOL:-1}"

export OMPI_MCA_pml=ob1
export OMPI_MCA_btl=self,tcp,vader

QE_BIN=pw.x
BANDS_BIN=bands.x
BASE_SCF_INPUT="../5_scf_U/scf.in"
PREFIX="MoS2"
U_VALUES=("0.0" "1.5" "3.0" "4.5")
OUTDIRS=("../tmp2/" "../tmp3/" "../tmp4/" "../tmp5/")

write_kpath() {
    cat <<'KPATH'
K_POINTS crystal_b
8
0.000000  0.000000  0.000000  10  ! Gamma
0.500000  0.000000  0.000000  10  ! M
0.333333  0.333333  0.000000  10  ! K
0.000000  0.000000  0.000000  10  ! Gamma
0.000000  0.000000  0.500000  10  ! A
0.500000  0.000000  0.500000  10  ! L
0.333333  0.333333  0.500000  10  ! H
0.000000  0.000000  0.500000   1  ! A
KPATH
}

for idx in "${!U_VALUES[@]}"; do
    U_VALUE="${U_VALUES[$idx]}"
    OUTDIR="${OUTDIRS[$idx]}"
    TAG="U${U_VALUE}"
    BAND_INPUT="bands_${TAG}.in"
    BAND_OUTPUT="bands_${TAG}.out"
    BANDS_PP_INPUT="bands_pp_${TAG}.in"
    BANDS_PP_OUTPUT="bands_pp_${TAG}.out"
    FILBAND="MoS2_bands_${TAG}.dat"
    GNU_FILE="${FILBAND}.gnu"

    if [ ! -f "${OUTDIR}/${PREFIX}.save/data-file-schema.xml" ]; then
        echo "Error: SCF 결과 없음 (${OUTDIR}). run_scf_node.sh 먼저 실행."
        continue
    fi

    # scf.in → bands 입력 (구 문법 lda_plus_u, calculation='bands')
    awk -v outdir="${OUTDIR}" -v uval="${U_VALUE}" '
        BEGIN { in_system=0; skip_rest=0; skip_hub=0 }
        skip_rest { next }
        /^[[:space:]]*calculation[[:space:]]*=/ { print "    calculation = '\''bands'\''"; next }
        /^[[:space:]]*outdir[[:space:]]*=/ { print "    outdir = '\''" outdir "'\''"; next }
        /^[[:space:]]*&system/ { in_system=1; print; next }
        in_system && /^[[:space:]]*\// {
            print "    nbnd = 32"
            if (uval+0 > 0) {
                print "    lda_plus_u = .true."
                print "    Hubbard_U(1) = " uval
                print "    U_projection_type = '\''ortho-atomic'\''"
            }
            in_system=0; print; next
        }
        /^K_POINTS/ { skip_rest=1; next }
        /^HUBBARD([[:space:]]|\()/ { skip_hub=1; next }
        skip_hub && /^[[:space:]]*(U|J0|J|V|ALPHA)[[:space:]]+/ { next }
        skip_hub { skip_hub=0 }
        { print }
    ' "${BASE_SCF_INPUT}" > "${BAND_INPUT}"
    write_kpath >> "${BAND_INPUT}"

    cat > "${BANDS_PP_INPUT}" <<EOF
&bands
    prefix = '${PREFIX}'
    outdir = '${OUTDIR}'
    filband = '${FILBAND}'
    lsym = .false.
/
EOF
    rm -f "${FILBAND}" "${GNU_FILE}" "${FILBAND}.rap"

    echo "[U=${U_VALUE}] bands (npool=${NPOOL})"
    $QE_MPIRUN ${QE_BIN} -npool ${NPOOL} < "${BAND_INPUT}" > "${BAND_OUTPUT}"
    if ! grep -q "End of band structure calculation" "${BAND_OUTPUT}"; then
        echo "  Error: pw.x bands 실패 (U=${U_VALUE})"; tail -n 20 "${BAND_OUTPUT}"; continue
    fi
    # bands.x는 병렬 이득 없어 npool 없이
    $QE_MPIRUN ${BANDS_BIN} < "${BANDS_PP_INPUT}" > "${BANDS_PP_OUTPUT}"
    [ -s "${GNU_FILE}" ] && echo "  Done: ${GNU_FILE}" || echo "  Error: ${GNU_FILE} 비어있음"
done
echo "All node band calc finished."
