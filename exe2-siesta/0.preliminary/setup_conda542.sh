#!/usr/bin/env bash
# py4siesta를 conda542 환경에서 사용할 수 있게 설치하는 스크립트
# 사용법:  bash setup_conda542.sh
set -euo pipefail

ENV_NAME="conda542"
USERBASE="$HOME/.local542"
WORKDIR="$HOME/ESC2026/exe2-siesta/0.preliminary"
REPO_URL="https://github.com/YHKlab-RGLee/py4siesta.git"
REPO_DIR="$WORKDIR/py4siesta"

# 1. conda542 활성화 (conda가 PATH에 없어도 동작하도록 base 탐색)
if command -v conda >/dev/null 2>&1; then
  CONDA_BASE="$(conda info --base)"
else
  for c in "$HOME/miniconda3" "$HOME/anaconda3" /opt/miniconda3 /opt/anaconda3; do
    [ -f "$c/etc/profile.d/conda.sh" ] && CONDA_BASE="$c" && break
  done
fi
if [ -z "${CONDA_BASE:-}" ] || [ ! -f "$CONDA_BASE/etc/profile.d/conda.sh" ]; then
  echo "ERROR: conda를 찾을 수 없습니다. CONDA_BASE 경로를 확인하세요." >&2
  exit 1
fi
source "$CONDA_BASE/etc/profile.d/conda.sh"
conda activate "$ENV_NAME"

# 2. 설치 위치를 본인 소유 폴더로 지정
export PYTHONUSERBASE="$USERBASE"
mkdir -p "$PYTHONUSERBASE"

# 3. pip 부트스트랩 (conda542 python에 pip이 없을 때만)
if ! python -m pip --version >/dev/null 2>&1; then
  echo ">>> pip 부트스트랩 중..."
  tmp_getpip="$(mktemp --suffix=.py)"
  curl -sS -o "$tmp_getpip" https://bootstrap.pypa.io/get-pip.py
  python "$tmp_getpip" --user
  rm -f "$tmp_getpip"
fi

# 4. py4siesta 내려받기 (없을 때만)
mkdir -p "$WORKDIR"
if [ ! -d "$REPO_DIR" ]; then
  echo ">>> py4siesta 클론 중..."
  git clone "$REPO_URL" "$REPO_DIR"
fi

# 5. 설치
echo ">>> py4siesta 설치 중..."
python -m pip install --user "$REPO_DIR"

# 6. .bashrc에 영구 설정 추가 (중복 방지)
add_line() { grep -qxF "$1" "$HOME/.bashrc" || echo "$1" >> "$HOME/.bashrc"; }
add_line "export PYTHONUSERBASE=\"\$HOME/.local542\""
add_line "export PATH=\"\$HOME/.local542/bin:\$PATH\""
add_line "export PATH=\"$REPO_DIR/scripts:\$PATH\""

# 7. 확인
export PATH="$USERBASE/bin:$PATH"
echo ">>> 설치 검증"
python -c "import py4siesta; print('py4siesta import OK')"
command -v py4siesta >/dev/null 2>&1 && echo "py4siesta CLI OK ($(command -v py4siesta))" || echo "CLI 경로 확인 필요"

echo
echo "=== 완료 ==="
echo "새 터미널을 열거나 'source ~/.bashrc' 후 'conda activate $ENV_NAME' 하면 바로 사용 가능합니다."
