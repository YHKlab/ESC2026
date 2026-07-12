#!/usr/bin/env bash
set -e

git clone https://github.com/YHKlab-RGLee/py4siesta.git
cd py4siesta

cat > ./NanoCore/env.py <<'EOF'
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

INSTALL_PREFIX="$HOME/opt/py4siesta"
mkdir -p "$INSTALL_PREFIX"

python -m pip install --prefix "$INSTALL_PREFIX" .

SITE_PACKAGES=$(find "$INSTALL_PREFIX/lib" \
    -type d -path '*/site-packages' | head -n 1)

grep -qxF "export PATH=\"$(pwd)/scripts:\${PATH}\"" ~/.bashrc || \
    echo "export PATH=\"$(pwd)/scripts:\${PATH}\"" >> ~/.bashrc

grep -qxF 'export PATH="$HOME/opt/py4siesta/bin:$PATH"' ~/.bashrc || \
    echo 'export PATH="$HOME/opt/py4siesta/bin:$PATH"' >> ~/.bashrc

grep -qxF "export PYTHONPATH=\"$SITE_PACKAGES:\${PYTHONPATH:-}\"" ~/.bashrc || \
    echo "export PYTHONPATH=\"$SITE_PACKAGES:\${PYTHONPATH:-}\"" >> ~/.bashrc
