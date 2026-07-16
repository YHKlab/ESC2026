#!/usr/bin/bash
CWD=$(pwd)
echo "1. Install xml"
wget https://launchpad.net/xmlf90/trunk/1.5/+download/xmlf90-1.5.4.tar.gz
tar xvzf xmlf90-1.5.4.tar.gz
mkdir libs
cd xmlf90-1.5.4
echo "./configure --prefix=${CWD}/libs"
./configure --prefix=${CWD}/libs
make -j4
make install
echo "2. Install libgrid"
cd ${CWD}
wget https://launchpad.net/libgridxc/trunk/0.7/+download/libgridxc-0.7.6.tgz
tar xvzf libgridxc-0.7.6.tgz
cd libgridxc-0.7.6
mkdir Gfortran
cp extra/fortran.mk Gfortran
cd Gfortran
sh ../src/config.sh         # this makes makefile
make
echo "3. atom install"
cd ${CWD}
wget https://siesta-project.org/SIESTA_MATERIAL/Pseudos/Code/atom-4.2.7-100.tgz
tar xvzf atom-4.2.7-100.tgz
cd atom-4.2.7-100
#cp arch.make.sample arch.make
cp ../patch/arch.make .
make
cd ${CWD}
