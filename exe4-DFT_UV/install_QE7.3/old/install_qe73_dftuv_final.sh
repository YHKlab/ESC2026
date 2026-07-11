#!/bin/bash
# ============================================================
# QE 7.3 + DFT-U-V (eACBN0) 통합 설치 스크립트
#   conda 환경 구축 → 컴파일러/openblas/patch 설치 → 소스 빌드
#   빌드 성공 후 BASE 아래의 cal_es.sh / QE 실행 .sh 파일 QE_BIN 자동 수정
#
# 폴더 구조 가정:
#   BASE/
#     1.Si/1.PBE/cal_es.sh
#     2.NiO/2.LDA/cal_es.sh
#     install_QE7.3/이_스크립트.sh
#
# 실행 위치는 어디여도 가능하지만, 이 스크립트 파일은 반드시
#   BASE/install_QE7.3/
# 안에 두는 것을 기준으로 한다.
# ============================================================
set -euo pipefail

ENV_NAME="qe73_ehub"

# 이 스크립트가 있는 폴더: BASE/install_QE7.3
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 실제 예제/계산 폴더들이 있는 최상위: BASE
PROJECT_BASE="$(cd "$SCRIPT_DIR/.." && pwd)"

# QE 소스/빌드 폴더는 최신 통합본과 동일하게 기본값을 HOME/qe73_build로 둔다.
# 필요하면 실행할 때 QE_BUILD_ROOT를 바꿀 수 있다.
#   QE_BUILD_ROOT="$SCRIPT_DIR/qe73_build" bash install_qe73_dftuv_unified_patch_cal_es.sh
BUILD_ROOT="${QE_BUILD_ROOT:-$HOME/qe73_build}"
QE_DIR="$BUILD_ROOT/q-e"
PATCH_REPO="$BUILD_ROOT/DFT-U-V"
NPROC="${MAKE_JOBS:-$(nproc 2>/dev/null || echo 4)}"

log() {
    echo
    echo "================================================"
    echo "$1"
    echo "================================================"
}

fail() {
    echo
    echo "❌ ERROR: $1" >&2
    exit 1
}

log "QE 7.3 + DFT-U-V 통합 설치"
echo "SCRIPT_DIR   = $SCRIPT_DIR"
echo "PROJECT_BASE = $PROJECT_BASE"
echo "BUILD_ROOT   = $BUILD_ROOT"
echo "QE_DIR       = $QE_DIR"
echo "MAKE_JOBS    = $NPROC"

# ---------- 1. Miniconda (없으면 설치) ----------
log "[1/8] Miniconda 확인/설치"
if [ ! -d "$HOME/miniconda3" ]; then
    mkdir -p "$HOME/miniconda3"
    wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O "$HOME/miniconda3/miniconda.sh"
    bash "$HOME/miniconda3/miniconda.sh" -b -u -p "$HOME/miniconda3"
    rm "$HOME/miniconda3/miniconda.sh"
fi

set +u  # conda 활성화 스크립트가 unbound var를 건드릴 수 있어 잠시 해제
source "$HOME/miniconda3/etc/profile.d/conda.sh"

# ToS 수락 (신버전 conda 대응)
if conda tos --help >/dev/null 2>&1; then
    conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main 2>/dev/null || true
    conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r 2>/dev/null || true
fi

# ---------- 2. 빌드 전용 conda 환경 ----------
log "[2/8] conda 환경 '$ENV_NAME' 생성/활성화"
if ! conda env list | awk '{print $1}' | grep -qx "$ENV_NAME"; then
    conda create -n "$ENV_NAME" -c conda-forge -y \
        gcc_linux-64=12.* gxx_linux-64=12.* gfortran_linux-64=12.* \
        binutils_linux-64 openblas fftw make patch wget git gnuplot python
fi
conda activate "$ENV_NAME"
if ! command -v x86_64-conda-linux-gnu-ar >/dev/null 2>&1; then
    echo "binutils_linux-64 missing in existing env; installing..."
    conda install -c conda-forge -y binutils_linux-64
fi
set -u

export PATH="$CONDA_PREFIX/bin:$PATH"

# 짧은 컴파일러 이름 심볼릭 링크: configure/make.inc가 gcc/gfortran/cpp 이름으로 찾을 때를 대비
ln -sf "$CONDA_PREFIX/bin/x86_64-conda-linux-gnu-gfortran" "$CONDA_PREFIX/bin/gfortran"
ln -sf "$CONDA_PREFIX/bin/x86_64-conda-linux-gnu-gcc"      "$CONDA_PREFIX/bin/gcc"
ln -sf "$CONDA_PREFIX/bin/x86_64-conda-linux-gnu-g++"      "$CONDA_PREFIX/bin/g++"
ln -sf "$CONDA_PREFIX/bin/x86_64-conda-linux-gnu-ar"       "$CONDA_PREFIX/bin/ar"
ln -sf "$CONDA_PREFIX/bin/x86_64-conda-linux-gnu-ranlib"   "$CONDA_PREFIX/bin/ranlib"

if [ -x "$CONDA_PREFIX/bin/x86_64-conda-linux-gnu-cpp" ]; then
    ln -sf "$CONDA_PREFIX/bin/x86_64-conda-linux-gnu-cpp" "$CONDA_PREFIX/bin/cpp"
fi

echo "gfortran: $(gfortran --version | head -1)"
echo "gcc     : $(gcc --version | head -1)"
echo "ar      : $(command -v ar)"
echo "gnuplot : $(command -v gnuplot || echo 'not found')"

# ---------- 3. 소스 clone ----------
log "[3/8] QE 7.3 + DFT-U-V 소스 준비"
mkdir -p "$BUILD_ROOT"
cd "$BUILD_ROOT"

if [ ! -d "$QE_DIR/.git" ]; then
    git clone -b qe-7.3 https://gitlab.com/QEF/q-e.git "$QE_DIR"
else
    echo "QE source already exists: $QE_DIR"
fi

if [ ! -d "$PATCH_REPO/.git" ]; then
    git clone https://github.com/KIAS-CMT/DFT-U-V.git "$PATCH_REPO"
else
    echo "DFT-U-V repo already exists: $PATCH_REPO"
fi

[ -f "$PATCH_REPO/qe-7.3_ehub_uv.diff" ] || fail "Patch file not found: $PATCH_REPO/qe-7.3_ehub_uv.diff"

# ---------- 4. configure (openblas 명시) ----------
log "[4/8] configure (openblas로 BLAS/LAPACK 지정)"
cd "$QE_DIR"
unset LD LD_LIBRARY_PATH MKLROOT MKL_HOME CPATH INCLUDE LIBRARY_PATH 2>/dev/null || true

export FC=gfortran
export F90=gfortran
export F77=gfortran
export CC=gcc
export CPP="gcc -E"
export BLAS_LIBS="-L$CONDA_PREFIX/lib -lopenblas"
export LAPACK_LIBS="-L$CONDA_PREFIX/lib -lopenblas"
export FFTW_LIBS="-L$CONDA_PREFIX/lib -lfftw3"

./configure \
    --with-internal-blas=no --with-internal-lapack=no \
    F90="$FC" F77="$F77" CC="$CC" \
    BLAS_LIBS="$BLAS_LIBS" LAPACK_LIBS="$LAPACK_LIBS" \
    2>&1 | tee "$BUILD_ROOT/configure.log"

# ---------- 5. make.inc 자동 보정 ----------
log "[5/8] make.inc 보정"
python3 - "$CONDA_PREFIX" << 'PYEOF'
import re
import sys
from pathlib import Path

conda = sys.argv[1]
p = Path("make.inc")
text = p.read_text()
lines = text.splitlines()
out = []
has_cpp = False

for line in lines:
    # 컴파일러/전처리기: Edison VSCode에서 cpp/gcc 탐색 문제가 나도 gcc -E로 통과
    if re.match(r"^\s*F90\s*=", line):
        line = "F90            = gfortran"
    elif re.match(r"^\s*F77\s*=", line):
        line = "F77            = gfortran"
    elif re.match(r"^\s*CC\s*=", line):
        line = "CC             = gcc"
    elif re.match(r"^\s*LD\s*=", line):
        line = "LD             = gfortran"
    elif re.match(r"^\s*CPP\s*=", line):
        line = "CPP            = gcc -E"
        has_cpp = True

    # 긴 줄 허용 + 최신 gfortran argument mismatch 완화
    if re.match(r"^\s*FFLAGS\s*=", line) or re.match(r"^\s*FFLAGS_NOOPT\s*=", line):
        for flag in ["-ffree-line-length-none", "-fallow-argument-mismatch"]:
            if flag not in line:
                line = line.rstrip() + " " + flag

    # BLAS/LAPACK: openblas 하나로 통일
    if re.match(r"^\s*BLAS_LIBS\s*=", line):
        line = f"BLAS_LIBS      = -L{conda}/lib -lopenblas"
    elif re.match(r"^\s*LAPACK_LIBS\s*=", line):
        line = f"LAPACK_LIBS    = -L{conda}/lib -lopenblas"

    out.append(line.rstrip())

if not has_cpp:
    out.append("CPP            = gcc -E")

p.write_text("\n".join(out) + "\n")
print("make.inc 수정 완료")
PYEOF

echo "--- make.inc 주요 항목 확인 ---"
grep -E "^(F90|F77|CC|LD|CPP|FFLAGS|FFLAGS_NOOPT|BLAS_LIBS|LAPACK_LIBS)\s*=" make.inc || true

# ---------- 6. patch 적용 ----------
log "[6/8] DFT-U-V patch 적용"
cp "$PATCH_REPO/qe-7.3_ehub_uv.diff" "$QE_DIR/"

if patch -p1 --dry-run < qe-7.3_ehub_uv.diff >/dev/null 2>&1; then
    patch -p1 < qe-7.3_ehub_uv.diff
    echo "patch 성공"
elif patch -p1 -R --dry-run < qe-7.3_ehub_uv.diff >/dev/null 2>&1; then
    echo "patch가 이미 적용되어 있음. 건너뜀."
else
    fail "DFT-U-V patch 적용 실패. 확인: cd $QE_DIR && patch -p1 --dry-run < qe-7.3_ehub_uv.diff"
fi

# ---------- 7. build ----------
log "[7/8] 빌드: make pw pp (-j$NPROC)"
# 이전 빌드 실패 흔적(.o)이 있으면 새 FFLAGS가 안 먹으니 정리
if find . -name '*.o' -print -quit | grep -q .; then
    echo "이전 오브젝트 발견 → make clean"
    make clean >/dev/null 2>&1 || true
fi

make depend 2>/dev/null || true
make -j"$NPROC" pw pp 2>&1 | tee "$BUILD_ROOT/make.log"

# ---------- 8. cal_es.sh / QE 실행 스크립트 자동 수정 ----------
log "[8/8] BASE 아래 cal_es.sh / QE 실행 .sh 파일 QE_BIN 자동 수정"

if [ ! -x "$QE_DIR/bin/pw.x" ]; then
    fail "pw.x 생성 실패. $BUILD_ROOT/make.log 확인 필요."
fi

QE_BIN="$QE_DIR/bin"
export QE_BIN

python3 - "$PROJECT_BASE" "$SCRIPT_DIR" "$QE_BIN" << 'PYEOF'
import os
import re
import stat
import sys
from pathlib import Path

project_base = Path(sys.argv[1]).resolve()
install_dir = Path(sys.argv[2]).resolve()
qe_bin = sys.argv[3]

marker_start = "# >>> QE_BIN auto-set by install_QE7.3"
marker_end = "# <<< QE_BIN auto-set by install_QE7.3"
block = f'''{marker_start}
QE_BIN="{qe_bin}"
pw_path="$QE_BIN"
export QE_BIN pw_path
{marker_end}
'''

qe_tokens = [
    "pw.x", "bands.x", "dos.x", "projwfc.x", "pp.x", "plotband.x",
    "workspace/q-e/bin", "qe73_build/q-e/bin", "pw_path", "QE_BIN"
]

candidates = []
for path in project_base.rglob("*.sh"):
    path = path.resolve()
    if path == install_dir or install_dir in path.parents:
        continue
    try:
        text = path.read_text(errors="ignore")
    except Exception:
        continue

    # 기본은 cal_es.sh 전체. 추가로 QE 실행 파일을 직접 부르는 .sh도 함께 보정.
    if path.name == "cal_es.sh" or any(tok in text for tok in qe_tokens):
        candidates.append(path)

changed = []
unchanged = []

for path in sorted(set(candidates)):
    text = path.read_text(errors="ignore")
    original = text

    # 기존 자동 삽입 블록 제거
    text = re.sub(
        rf"\n?{re.escape(marker_start)}.*?{re.escape(marker_end)}\n?",
        "\n",
        text,
        flags=re.S,
    )

    # 기존 QE_BIN/pw_path 직접 지정 제거. 새 블록 하나로 통일.
    kept_lines = []
    for line in text.splitlines():
        if re.match(r"^\s*(export\s+)?(QE_BIN|pw_path)\s*=", line):
            continue
        if re.match(r"^\s*export\s+(QE_BIN|pw_path)\s*$", line):
            continue
        kept_lines.append(line)
    text = "\n".join(kept_lines).rstrip() + "\n"

    # 오래된 hard-coded QE 경로를 변수 기반으로 치환
    text = text.replace("~/workspace/q-e/bin/", "${QE_BIN}/")
    text = re.sub(r"/home/[^/\s\"']+/workspace/q-e/bin/", "${QE_BIN}/", text)
    text = re.sub(r"/home/[^/\s\"']+/qe73_build/q-e/bin/", "${QE_BIN}/", text)
    text = re.sub(r"\$pw_path/", "${QE_BIN}/", text)
    text = re.sub(r"\$\{pw_path\}/", "${QE_BIN}/", text)

    # shebang 다음에 QE_BIN 블록 삽입
    lines = text.splitlines()
    if lines and lines[0].startswith("#!"):
        text = lines[0] + "\n" + block + "\n" + "\n".join(lines[1:]).rstrip() + "\n"
    else:
        text = block + "\n" + text

    if text != original:
        path.write_text(text)
        mode = path.stat().st_mode
        path.chmod(mode | stat.S_IXUSR)
        changed.append(path)
    else:
        unchanged.append(path)

print(f"PROJECT_BASE = {project_base}")
print(f"QE_BIN       = {qe_bin}")
print("")
print("수정된 스크립트:")
if changed:
    for p in changed:
        print("  " + str(p.relative_to(project_base)))
else:
    print("  none")

print("")
print("검사 대상이었지만 변경 없음:")
if unchanged:
    for p in unchanged:
        print("  " + str(p.relative_to(project_base)))
else:
    print("  none")
PYEOF

# ---------- 최종 검증 출력 ----------
echo
if [ -x "$QE_DIR/bin/pw.x" ]; then
    echo "================================================"
    echo " ✅ 빌드 성공!"
    echo "   pw.x   : $QE_DIR/bin/pw.x"
    echo "   bands.x: $QE_DIR/bin/bands.x"
    echo
    echo " ✅ 계산 스크립트 QE_BIN 자동 수정 완료"
    echo "   BASE  : $PROJECT_BASE"
    echo "   QE_BIN=$QE_DIR/bin"
    echo "================================================"
else
    fail "pw.x 생성 실패. $BUILD_ROOT/make.log 확인 필요."
fi
