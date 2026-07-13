#!/bin/bash

wannier90.x --pp Fe

mpirun -np 4 pw2wannier90.x -inp Fe.pw2wan.in > Fe.pw2wan.out
wannier90.x Fe