#!/usr/bin/env bash
set -e

git clone https://github.com/YHKlab-RGLee/py4siesta.git
cd py4siesta

python -m pip install --user .

grep -qxF 'export PATH="$HOME/.local/bin:$PATH"' ~/.bashrc || \
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

grep -qxF "export PATH=\"$(pwd)/scripts:\${PATH}\"" ~/.bashrc || \
echo "export PATH=\"$(pwd)/scripts:\${PATH}\"" >> ~/.bashrc

cd ..
cat > ./py4siesta/NanoCore/env.py <<'EOF'
#
# SIESTA
#

siesta_calculator = '/opt/siesta-5.4.2-install/bin/siesta'
siesta_psf_location = ''
siesta_util_location = '/opt/siesta-5.4.2-install/bin/'
siesta_util_band = 'gnubands'
siesta_util_dos  = 'Eig2DOS'
siesta_util_pdos = 'fmpdos'
siesta_util_rho  = 'rho2xsf'
siesta_util_vh   = 'macroave'
siesta_util_pldos = ''
EOF
