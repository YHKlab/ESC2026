#!/bin/bash
# ============================================================
#  Quantum ESPRESSO 설치 (conda-forge 바이너리, 컴파일 불필요)
#
#  특징: $HOME 을 오염시키지 않음 — 모든 것이 exe3-qe 폴더 안에
#    - miniconda      → exe3-qe/.local/miniconda3
#    - conda env      → exe3-qe/.local/env        (prefix env)
#    - conda 메타데이터 → exe3-qe/.local/condahome, .local/cache, .local/pkgs
#      (~/.conda, ~/.cache/conda, ~/.anaconda 로 새는 것까지 전부 봉인)
#    - conda init 실행 안 함 (~/.bashrc 미수정)
#
#  사용법:  bash 0_setup/install_qe7.4.sh
#  설치 후: source setup_env.sh   (계산 전 매번)
# ============================================================
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"          # exe3-qe

LOCAL="$ROOT/.local"
CONDA_HOME="$LOCAL/miniconda3"
ENV_PREFIX="$LOCAL/env"
# conda 가 사용자별로 HOME 에 남기는 흔적을 폴더 안에 가두기 위한 경로
CONDA_HOMEDIR="$LOCAL/condahome"
CONDA_CACHE="$LOCAL/cache"
CONDA_PKGS="$LOCAL/pkgs"
mkdir -p "$LOCAL" "$CONDA_HOMEDIR" "$CONDA_CACHE" "$CONDA_PKGS"

# 모든 conda 호출을 이 wrapper 로 감싸면 ~/.conda, ~/.cache, ~/.anaconda 오염 없음
run_conda() {
    env HOME="$CONDA_HOMEDIR" \
        XDG_CACHE_HOME="$CONDA_CACHE" \
        CONDA_PKGS_DIRS="$CONDA_PKGS" \
        "$@"
}

echo "================================================"
echo " 실습용 QE 설치 (약 3~5분)"
echo "   설치 위치: $ROOT   (HOME 오염 없음)"
echo "================================================"

# ---------- 1. Miniconda (폴더 안에) ----------
echo "[1/3] Miniconda (프로젝트 내부)"
if [ ! -x "$CONDA_HOME/bin/conda" ]; then
    wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
        -O "$LOCAL/miniconda.sh"
    # -b 배치, -p 경로 지정. conda init 은 실행하지 않음 (~/.bashrc 미수정)
    HOME="$CONDA_HOMEDIR" bash "$LOCAL/miniconda.sh" -b -u -p "$CONDA_HOME"
    rm -f "$LOCAL/miniconda.sh"
    echo "  설치됨: $CONDA_HOME"
else
    echo "  이미 존재 → 건너뜀"
fi

set +u
source "$CONDA_HOME/etc/profile.d/conda.sh"
# ToS 수락 (신버전 conda) — 두 채널 모두
run_conda conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main 2>/dev/null || true
run_conda conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r    2>/dev/null || true

# ---------- 2. QE + 플로팅 패키지 (prefix env = 폴더 안에) ----------
echo "[2/3] Quantum ESPRESSO 환경 (prefix: $ENV_PREFIX)"
if [ ! -x "$ENV_PREFIX/bin/pw.x" ]; then
    # qe 와 함께 matplotlib/ase/numpy 도 env 안에 설치 → pip(HOME) 불필요
    run_conda conda create -p "$ENV_PREFIX" --override-channels -c conda-forge -y \
        qe matplotlib numpy ase
fi
set -u

# ---------- 3. setup_env.sh 생성 (초경량 활성화, HOME 미사용) ----------
echo "[3/3] setup_env.sh 생성"
cat > "$ROOT/setup_env.sh" << 'ENVEOF'
#!/bin/bash
# 계산 전 매번:  source setup_env.sh
# conda activate 를 쓰지 않고 PATH/LD 만 잡음 → 실행 중 HOME 을 건드리지 않음
_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_ENV="$_ROOT/.local/env"
if [ ! -x "$_ENV/bin/pw.x" ]; then
    echo "  [setup_env] QE 미설치. 먼저:  bash 0_setup/install_qe7.4.sh" >&2
    return 1 2>/dev/null || exit 1
fi
export PATH="$_ENV/bin:${PATH:-}"
export LD_LIBRARY_PATH="$_ENV/lib:${LD_LIBRARY_PATH:-}"
# conda 캐시류도 폴더 안으로 (혹시라도 하위 도구가 conda 를 부를 때 대비)
export CONDA_PKGS_DIRS="$_ROOT/.local/pkgs"
export XDG_CACHE_HOME="$_ROOT/.local/cache"
echo "환경 준비 완료:  pw.x = $(command -v pw.x)"
ENVEOF
chmod +x "$ROOT/setup_env.sh"

echo ""
if [ -x "$ENV_PREFIX/bin/pw.x" ]; then
    echo "================================================"
    echo " ✅ 설치 완료"
    echo "   pw.x : $ENV_PREFIX/bin/pw.x"
    echo ""
    echo " 다음 단계 (새 터미널 불필요):"
    echo "   cd $ROOT"
    echo "   source setup_env.sh"
    echo "   cd 1_relax && bash run_all.sh"
    echo "================================================"
else
    echo "ERROR: pw.x 생성 실패"
    exit 1
fi
