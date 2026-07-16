#!/bin/bash
# ============================================================
#  DFT+U+V 실습 환경 통합 설치 (한 파일로 완결)
#
#  특징: $HOME 을 전혀 오염시키지 않음
#    - miniconda   → exe4-DFT_UV/.local/miniconda3
#    - conda env   → exe4-DFT_UV/.local/env       (prefix env)
#    - QE 소스/빌드 → exe4-DFT_UV/qe73_build/q-e
#
#  사용법:  bash install_all.sh
#  설치 후: source setup_env.sh   (계산 전 매번)
# ============================================================
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"        # exe4-DFT_UV

LOCAL="$ROOT/.local"
CONDA_HOME="$LOCAL/miniconda3"
ENV_PREFIX="$LOCAL/env"
QE_BUILD="$ROOT/qe73_build"
QE_DIR="$QE_BUILD/q-e"
NPROC="$(nproc 2>/dev/null || echo 4)"

# --- 옵션 처리 ---
#   (없음)        : 이어서 설치 (설치된 단계는 skip, 빌드는 증분) — 오류 후 그냥 다시 실행하면 됨
#   --rebuild-qe  : QE 소스/빌드만 삭제 후 재빌드 (conda 환경은 유지 → 빠름)
#   --fresh       : .local 포함 전부 삭제 후 처음부터
FRESH=0; REBUILD_QE=0
for arg in "$@"; do
  case "$arg" in
    --fresh)       FRESH=1 ;;
    --rebuild-qe)  REBUILD_QE=1 ;;
    -h|--help) echo "사용법: bash install_all.sh [--fresh | --rebuild-qe]"; exit 0 ;;
    *) echo "알 수 없는 옵션: $arg (무시)";;
  esac
done
if [ "$FRESH" = 1 ]; then
    echo "  --fresh: 전체 삭제 후 재설치 (.local, qe73_build)"
    rm -rf "$LOCAL" "$QE_BUILD" "$ROOT/setup_env.sh"
elif [ "$REBUILD_QE" = 1 ]; then
    echo "  --rebuild-qe: QE 소스/빌드만 삭제 (conda 환경 유지)"
    rm -rf "$QE_BUILD"
fi

# --- conda 흔적(~/.conda, ~/.cache/conda, ~/.anaconda)을 폴더 안에 봉인 ---
# 단, git clone 은 사용자의 실제 ~/.gitconfig(프록시/SSL 등)가 필요하므로
# HOME 재지정은 conda 사용 구간에만 적용하고 clone 전에 원복한다.
REAL_HOME="$HOME"
CONDA_HOMEDIR="$LOCAL/condahome"
export XDG_CACHE_HOME="$LOCAL/cache"     # git 에 무해
export CONDA_PKGS_DIRS="$LOCAL/pkgs"     # git 에 무해
mkdir -p "$CONDA_HOMEDIR" "$XDG_CACHE_HOME" "$CONDA_PKGS_DIRS"

echo "=================================================="
echo " DFT+U+V 실습 환경 설치"
echo "   설치 위치: $ROOT   (HOME 오염 없음)"
echo "   예상 시간: 20~40분"
echo "=================================================="

# ---------- 1. Miniconda (폴더 안에) ----------
echo "[1/6] Miniconda (프로젝트 내부)"
if [ ! -x "$CONDA_HOME/bin/conda" ]; then
    mkdir -p "$CONDA_HOME"
    wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
        -O "$LOCAL/miniconda.sh"
    HOME="$CONDA_HOMEDIR" bash "$LOCAL/miniconda.sh" -b -u -p "$CONDA_HOME"
    rm -f "$LOCAL/miniconda.sh"
    echo "  설치됨: $CONDA_HOME"
else
    echo "  이미 존재 → 건너뜀"
fi

set +u
export HOME="$CONDA_HOMEDIR"        # conda 구간만 봉인 (clone 전 원복)
source "$CONDA_HOME/etc/profile.d/conda.sh"
# ToS 수락 (신버전 conda)
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main 2>/dev/null || true
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r    2>/dev/null || true

# ---------- 2. conda env (prefix 방식 = 폴더 안에) ----------
echo "[2/6] conda 환경 (prefix: $ENV_PREFIX)"
if [ ! -d "$ENV_PREFIX/bin" ]; then
    conda create -p "$ENV_PREFIX" -c conda-forge -y \
        gcc_linux-64=12.* gxx_linux-64=12.* gfortran_linux-64=12.* \
        binutils_linux-64 openblas fftw make patch wget git gnuplot python
fi
conda activate "$ENV_PREFIX"
set -u

# 짧은 컴파일러/binutils 이름 링크
# (QE 본체는 conda 가 export 한 $AR 을 쓰지만, mbd.make 등 외부 makefile 은
#  'ar' 'ranlib' 을 하드코딩하므로 짧은 이름이 반드시 필요)
for t in gfortran gcc g++ ar ranlib ld nm strip; do
    src="$CONDA_PREFIX/bin/x86_64-conda-linux-gnu-$t"
    [ -x "$src" ] && ln -sf "$src" "$CONDA_PREFIX/bin/$t"
done
command -v ar >/dev/null || { echo "  ERROR: ar 준비 실패 (binutils 미설치?)"; exit 1; }
echo "  gfortran: $(gfortran --version | head -1)"

# clone/build 는 사용자의 실제 HOME(=git 설정, 프록시)로 수행
export HOME="$REAL_HOME"

# ---------- 3. 소스 clone (폴더 안에, shallow, 원자적) ----------
# 임시 폴더에 받고 성공 시에만 제자리로 이동 → 중단된 partial clone 이 다음 실행을 막지 않음
echo "[3/6] QE 7.3 + DFT-U-V patch 소스"
mkdir -p "$QE_BUILD" && cd "$QE_BUILD"
if [ ! -f "$QE_DIR/configure" ]; then
    rm -rf "$QE_DIR" "$QE_BUILD/q-e.tmp"
    echo "  q-e clone (shallow, qe-7.3) ..."
    { git -c advice.detachedHead=false clone --depth 1 -b qe-7.3 https://github.com/QEF/q-e.git q-e.tmp \
      || git -c advice.detachedHead=false clone --depth 1 -b qe-7.3 https://gitlab.com/QEF/q-e.git q-e.tmp; } \
      || { rm -rf "$QE_BUILD/q-e.tmp"; echo "  ERROR: QE 소스 clone 실패 (github/gitlab 모두). 네트워크/프록시 확인"; exit 1; }
    mv "$QE_BUILD/q-e.tmp" "$QE_DIR"
fi
[ -f "$QE_DIR/configure" ] || { echo "  ERROR: $QE_DIR 준비 실패 (configure 없음)"; exit 1; }
if [ ! -d "$QE_BUILD/DFT-U-V" ]; then
    rm -rf "$QE_BUILD/DFT-U-V.tmp"
    echo "  DFT-U-V patch clone ..."
    git clone --depth 1 https://github.com/KIAS-CMT/DFT-U-V.git "$QE_BUILD/DFT-U-V.tmp" \
      || { rm -rf "$QE_BUILD/DFT-U-V.tmp"; echo "  ERROR: DFT-U-V patch clone 실패"; exit 1; }
    mv "$QE_BUILD/DFT-U-V.tmp" "$QE_BUILD/DFT-U-V"
fi

# QE 외부 라이브러리 MBD(libmbd)는 git submodule → shallow clone 시 안 받아짐.
# pp(open_grid.x 등)가 MBD/libmbd.a 를 링크하므로 명시적으로 받는다.
if [ ! -f "$QE_DIR/external/mbd/Makefile" ]; then
    echo "  submodule: external/mbd (libmbd) ..."
    ( cd "$QE_DIR" && git submodule update --init external/mbd ) \
      || { echo "  ERROR: mbd submodule 받기 실패 (네트워크/프록시 확인)"; exit 1; }
fi
[ -f "$QE_DIR/external/mbd/Makefile" ] || { echo "  ERROR: external/mbd 준비 실패"; exit 1; }

# ---------- 4. configure ----------
echo "[4/6] configure (openblas 명시)"
cd "$QE_DIR"
unset LD LD_LIBRARY_PATH 2>/dev/null || true
export FC=gfortran F90=gfortran F77=gfortran CC=gcc
./configure \
    BLAS_LIBS="-L$CONDA_PREFIX/lib -lopenblas" \
    LAPACK_LIBS="-L$CONDA_PREFIX/lib -lopenblas" \
    > "$QE_BUILD/configure.log" 2>&1 || { echo "configure 실패 → $QE_BUILD/configure.log"; exit 1; }

# ---------- 5. make.inc 보정 + patch ----------
echo "[5/6] make.inc 보정 & patch 적용"
python3 - "$CONDA_PREFIX" << 'PYEOF'
import re, sys
from pathlib import Path
conda = sys.argv[1]
p = Path("make.inc"); out = []
for line in p.read_text().splitlines():
    if re.match(r"^\s*FFLAGS(_NOOPT)?\s*=", line):
        for flag in ("-ffree-line-length-none", "-fallow-argument-mismatch"):
            if flag not in line:
                line = line.rstrip() + " " + flag
    elif re.match(r"^\s*BLAS_LIBS\s*=", line):
        line = f"BLAS_LIBS      = -L{conda}/lib -lopenblas"
    elif re.match(r"^\s*LAPACK_LIBS\s*=", line):
        line = f"LAPACK_LIBS    = -L{conda}/lib -lopenblas"
    out.append(line)
p.write_text("\n".join(out) + "\n")
print("  make.inc OK")
PYEOF

cp "$QE_BUILD/DFT-U-V/qe-7.3_ehub_uv.diff" .
if patch -p1 --dry-run < qe-7.3_ehub_uv.diff >/dev/null 2>&1; then
    patch -p1 < qe-7.3_ehub_uv.diff >/dev/null
    echo "  patch 적용됨"
else
    echo "  patch 이미 적용 상태 → 건너뜀"
fi

# ---------- 6. build ----------
# QE 는 높은 -j 에서 모듈 의존성 레이스로 헛failure 가 잘 남 → 상한(16)을 두고
# pw 먼저, 그 다음 pp. 병렬 실패 시 직렬(-j1)로 재시도(레이스면 완성, 진짜 에러면 원인 노출).
JOBS=$(( NPROC > 16 ? 16 : NPROC ))
echo "[6/6] 빌드 (make pw → pp, -j$JOBS) — 시간이 걸립니다"
# 증분 빌드: 이전에 만들어진 오브젝트는 재사용 → 오류 후 다시 실행하면 이어서 진행.
# 처음부터 다시 빌드하려면:  bash install_all.sh --rebuild-qe
make depend >/dev/null 2>&1 || true

build_target() {   # $1 = pw | pp
    if make -j"$JOBS" "$1" >> "$QE_BUILD/make.log" 2>&1; then return 0; fi
    echo "  [$1] 병렬 빌드 실패 → 직렬(-j1) 재시도"
    if make "$1" >> "$QE_BUILD/make.log" 2>&1; then return 0; fi
    echo "  ❌ [$1] 빌드 실패 → $QE_BUILD/make.log 마지막 부분:"
    grep -i "error:" "$QE_BUILD/make.log" | tail -5
    tail -20 "$QE_BUILD/make.log"
    return 1
}

: > "$QE_BUILD/make.log"

# MBD(libmbd) 선빌드: extlibs 의 libmbd 규칙은 'MBD/ 폴더가 없을 때만' 빌드하는데,
# 이전 실패 실행이 빈 MBD/ 를 남기면 빌드를 영영 건너뛴다 → libmbd.a 가 안 생겨 pw/pp 링크 실패.
# libmbd.a 가 없으면 빈 MBD/ 를 제거하고 명시적으로 선빌드한다.
if [ ! -f "$QE_DIR/MBD/libmbd.a" ]; then
    rm -rf "$QE_DIR/MBD"
    echo "  libmbd 빌드 (external/mbd) ..."
    make libmbd >> "$QE_BUILD/make.log" 2>&1 \
      || { echo "  ❌ libmbd 빌드 실패 → $QE_BUILD/make.log"; grep -i "error" "$QE_BUILD/make.log" | tail -5; tail -20 "$QE_BUILD/make.log"; exit 1; }
    [ -f "$QE_DIR/MBD/libmbd.a" ] || { echo "  ❌ MBD/libmbd.a 생성 실패 → 로그 마지막:"; tail -20 "$QE_BUILD/make.log"; exit 1; }
fi

build_target pw || exit 1
build_target pp || exit 1

# ---------- setup_env.sh 생성 ----------
cat > "$ROOT/setup_env.sh" << 'ENVEOF'
#!/bin/bash
# 계산 전 매번:  source setup_env.sh
# conda activate 를 쓰지 않고 PATH/LD 만 잡음 → 실행 중 HOME 을 건드리지 않음
_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_ENV="$_ROOT/.local/env"
export QE_BIN="$_ROOT/qe73_build/q-e/bin"
export PATH="$QE_BIN:$_ENV/bin:${PATH:-}"
export LD_LIBRARY_PATH="$_ENV/lib:${LD_LIBRARY_PATH:-}"
export CONDA_PKGS_DIRS="$_ROOT/.local/pkgs"
export XDG_CACHE_HOME="$_ROOT/.local/cache"
echo "환경 준비 완료"
echo "  QE_BIN  = $QE_BIN"
echo "  gnuplot = $(command -v gnuplot)"
ENVEOF
chmod +x "$ROOT/setup_env.sh"

echo
if [ -x "$QE_DIR/bin/pw.x" ]; then
    echo "=================================================="
    echo " 설치 성공"
    echo "   pw.x    : $QE_DIR/bin/pw.x"
    echo "   bands.x : $QE_DIR/bin/bands.x"
    echo
    echo " 다음 단계:"
    echo "   cd $ROOT"
    echo "   source setup_env.sh"
    echo "   cd 1.Si/1.PBE && bash cal_es.sh"
    echo "=================================================="
else
    echo "pw.x 생성 실패 → $QE_BUILD/make.log 확인"
    exit 1
fi