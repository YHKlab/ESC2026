#!/bin/bash
set -e

cd $HOME

MINICONDA=$HOME/miniconda3
ENV_NAME=siesta415

echo "===== remove old miniconda ====="
rm -rf $MINICONDA
rm -rf ~/.conda ~/.continuum
rm -f ~/.condarc

echo "===== install fresh miniconda ====="
wget -O miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash miniconda.sh -b -p $MINICONDA

source $MINICONDA/etc/profile.d/conda.sh

conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main || true
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r || true

echo "===== create env ====="
conda create -y -n $ENV_NAME -c conda-forge python==3.11.5

conda activate $ENV_NAME

echo "===== install packages ====="
conda install -y -c conda-forge openmpi
conda install -y -c conda-forge "siesta=4.1.5=*openmpi*"

echo "===== check ====="
which python
python --version
which mpirun
mpirun --version | head -n 1
which siesta


echo ""
echo "======================================"
echo "SIESTA 4.1.5 conda binary install finished"
echo "Activate with:"
echo "source ~/miniconda3/etc/profile.d/conda.sh"
echo "conda activate $ENV_NAME"
echo "======================================"

source ~/miniconda3/etc/profile.d/conda.sh
conda activate siesta415

conda create -n plotting -c conda-forge python=3.11 matplotlib numpy -y
