#!/usr/bin/env bash
set -e

git clone https://github.com/YHKlab-RGLee/py4siesta.git
cd py4siesta

python -m pip install --user .

grep -qxF 'export PATH="$HOME/.local/bin:$PATH"' ~/.bashrc || \
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

grep -qxF "export PATH=\"$(pwd)/scripts:\${PATH}\"" ~/.bashrc || \
echo "export PATH=\"$(pwd)/scripts:\${PATH}\"" >> ~/.bashrc

source ~/.bashrc
