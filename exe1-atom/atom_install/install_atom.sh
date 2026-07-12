#!/usr/bin/bash

echo "1. Install xml"
wget https://launchpad.net/xmlf90/trunk/1.5/+download/xmlf90-1.5.4.tar.gz
tar xvzf xmlf90-1.5.4.tar.gz
mkdir libs
cd xmlf90-1.5.4
echo "./configure --prefix=$HOME/atom/libs"
./configure --prefix=$HOME/atom/libs
make -j4
make install
cd ..
echo "2. Install libgrid"
wget https://launchpad.net/libgridxc/trunk/0.7/+download/libgridxc-0.7.6.tgz
tar xvzf libgridxc-0.7.6.tgz
cd libgridxc-0.7.6
mkdir Gfortran
cp extra/fortran.mk Gfortran
cd Gfortran
sh ../src/config.sh         # this makes makefile
make
cd ../..
echo "3. atom install"
wget https://siesta-project.org/SIESTA_MATERIAL/Pseudos/Code/atom-4.2.7-100.tgz
tar xvzf atom-4.2.7-100.tgz
cd atom-4.2.7-100
#cp arch.make.sample arch.make
cp ../patch/arch.make .
make