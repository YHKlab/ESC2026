#!/bin/bash
set -e

cd $HOME

MINICONDA=$HOME/miniconda3
ENV_NAME=conda542

TARFILE=$HOME/siesta-5.4.2.tar.gz
SRC_DIR=$HOME/siesta-5.4.2
BUILD_DIR=$SRC_DIR/build
INSTALL_DIR=$HOME/siesta-5.4.2-install

if [ ! -f "$TARFILE" ]; then
    echo "ERROR: $TARFILE not found"
    exit 1
fi

echo "Removing old Miniconda..."
rm -rf $MINICONDA
rm -rf ~/.conda ~/.continuum
rm -f ~/.condarc

echo "Installing fresh Miniconda..."
wget -O miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash miniconda.sh -b -p $MINICONDA

source $MINICONDA/etc/profile.d/conda.sh

conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

echo "Creating conda environment: $ENV_NAME"

conda create -y -n $ENV_NAME \
    -c conda-forge \
    python=3.11.5 \
    cmake \
    make \
    pkg-config \
    binutils \
    binutils_impl_linux-64 \
    gcc_linux-64 \
    gxx_linux-64 \
    gfortran_linux-64 \
    openmpi \
    scalapack \
    libxc \
    fftw \
    blas \
    lapack

conda activate $ENV_NAME

echo "===== ENVIRONMENT ====="
which python
python --version
which cmake
cmake --version
which make
make --version | head -n 1
which mpicc
which mpif90
which ar || true
which ranlib || true
which x86_64-conda-linux-gnu-ar
which x86_64-conda-linux-gnu-ranlib
mpif90 --version | head -n 1
echo "CONDA_PREFIX=$CONDA_PREFIX"

cd $HOME
rm -rf $SRC_DIR
rm -rf $INSTALL_DIR
tar -xzf $TARFILE

rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR
cd $BUILD_DIR

cmake .. \
    -DCMAKE_INSTALL_PREFIX=$INSTALL_DIR \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_Fortran_COMPILER=mpif90 \
    -DCMAKE_C_COMPILER=mpicc \
    -DCMAKE_CXX_COMPILER=mpicxx \
    -DCMAKE_AR=$CONDA_PREFIX/bin/x86_64-conda-linux-gnu-ar \
    -DCMAKE_RANLIB=$CONDA_PREFIX/bin/x86_64-conda-linux-gnu-ranlib \
    -DSIESTA_WITH_MPI=ON \
    -DSIESTA_WITH_FLOOK=OFF \
    -DSIESTA_WITH_ELSI=OFF \
    -DSIESTA_WITH_NETCDF=OFF \
    -DSIESTA_WITH_WANNIER90=OFF \
    -DSIESTA_WITH_DFTD3=OFF \
    -DSIESTA_WITH_FFTW=ON \
    -DSIESTA_WITH_LIBXC=ON

make -j 8
make install

echo ""
echo "======================================"
echo "SIESTA 5.4.2 build finished"
echo "Executable:"
find $INSTALL_DIR -name "siesta" -type f
echo "======================================"
