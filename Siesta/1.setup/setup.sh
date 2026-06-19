#!/bin/bash
# 실습 환경 설정 스크립트
# 사용법: bash 1.setup/setup.sh

set -e

ENV_NAME="summer"

echo "=== SIESTA 2026 실습 환경 설정 ==="
echo ""

# conda 존재 확인
if ! command -v conda &> /dev/null; then
    echo "[error] conda가 설치되어 있지 않습니다."
    echo "  Miniforge: https://github.com/conda-forge/miniforge"
    exit 1
fi

# 환경 생성 (이미 있으면 스킵)
if conda env list | grep -q "^${ENV_NAME} "; then
    echo "[skip] conda 환경 '${ENV_NAME}' 이 이미 존재합니다."
else
    echo "[1/2] conda 환경 생성: ${ENV_NAME}"
    conda create -n "${ENV_NAME}" -c conda-forge \
        python=3.11 \
        sisl \
        ase \
        matplotlib \
        numpy \
        scipy \
        netcdf4 \
        -y
    echo ""
fi

# 설치 확인
echo "[2/2] 패키지 설치 확인"
conda run -n "${ENV_NAME}" python - <<'PYEOF'
import importlib, sys

packages = {
    "numpy":      "numpy",
    "matplotlib": "matplotlib",
    "scipy":      "scipy",
    "ase":        "ase",
    "sisl":       "sisl",
    "netCDF4":    "netCDF4",
}

ok = True
for name, mod in packages.items():
    try:
        m = importlib.import_module(mod)
        ver = getattr(m, "__version__", "?")
        print(f"  [ok] {name:<12} {ver}")
    except ImportError:
        print(f"  [!!] {name:<12} 설치 실패")
        ok = False

sys.exit(0 if ok else 1)
PYEOF

echo ""
echo "=== 완료 ==="
echo "환경 활성화:  conda activate ${ENV_NAME}"
echo "SIESTA 확인:  singularity exec /singularity/siesta_5.4.2.sif siesta --version"
