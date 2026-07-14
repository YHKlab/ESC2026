export PS1="\[\e[32m\]\u@\h:\[\e[34m\]\w\[\e[0m\] \$ "

alias ls='ls --color=auto'

# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/opt/miniconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/opt/miniconda3/etc/profile.d/conda.sh" ]; then
        . "/opt/miniconda3/etc/profile.d/conda.sh"
    else
        export PATH="/opt/miniconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<









export PATH="${HOME}/bin:$PATH"




# === EDISON_SIESTA_QE_ENV_MARKER_V3 ===
# Global Env for SIESTA & QE (Auto-generated)

ENV_NAME="conda542"
SIESTA_VERSION="5.4.2"
QE_VERSION="7.5"

export MINICONDA="/opt/miniconda3"
export CONDA_ENV="${ENV_NAME}"

if [ -f "${MINICONDA}/etc/profile.d/conda.sh" ]; then
    source "${MINICONDA}/etc/profile.d/conda.sh"

    if [ "${CONDA_DEFAULT_ENV:-}" != "${CONDA_ENV}" ]; then
        conda activate "${CONDA_ENV}"
    fi
fi

export SRC_DIR="/opt/siesta-${SIESTA_VERSION}"
export BUILD_DIR="/opt/siesta-${SIESTA_VERSION}/build"
export INSTALL_DIR="/opt/siesta-${SIESTA_VERSION}-install"

export PATH="${INSTALL_DIR}/bin:${PATH}"
export LD_LIBRARY_PATH="${CONDA_PREFIX}/lib:${LD_LIBRARY_PATH}"

export CC=x86_64-conda-linux-gnu-gcc
export CXX=x86_64-conda-linux-gnu-g++
export FC=x86_64-conda-linux-gnu-gfortran

export OMP_NUM_THREADS=1

# ===================================

