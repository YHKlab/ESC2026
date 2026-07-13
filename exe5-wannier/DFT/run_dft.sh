#!/bin/bash

mpirun -np 4 pw.x -inp Fe.scf.in > Fe.scf.out
mpirun -np 4 pw.x -inp Fe.band.in > Fe.band.out
mpirun -np 4 bands.x -inp Fe.bands.in > Fe.bands.out
mpirun -np 4 pw.x -inp Fe.nscf.in > Fe.nscf.out