#!/bin/bash
set -e

# coarse + fine scan
alist="2.70 2.80 2.85 2.875 2.90 2.925 2.95 3.00 3.10"

for a in $alist
do
    dir=a${a}
    mkdir -p $dir

    cp RUN.fdf BASIS.fdf KPT.fdf Au.psf run_slurm.sh $dir/

    # RUN.fdf: CG step 300
    sed -i '/MD.NumCGsteps/d' $dir/RUN.fdf
    sed -i '/SolutionMethod diagon/a MD.NumCGsteps 300' $dir/RUN.fdf

    # STRUCT.fdf: lattice constant만 변경, LatticeVectors는 예제 형태 유지
    cat > $dir/STRUCT.fdf << EOF2
LatticeConstant ${a} Ang

%block LatticeVectors
0.81649  0.28867   0.50000
0.00000  0.86602   0.50000
0.00000  0.00000   1.00000
%endblock LatticeVectors

NumberOfAtoms 1
NumberOfSpecies 1

%block ChemicalSpeciesLabel
1 79 Au
%endblock ChemicalSpeciesLabel

AtomicCoordinatesFormat Fractional

%block AtomicCoordinatesAndAtomicSpecies
0.0 0.0 0.0 1
%endblock AtomicCoordinatesAndAtomicSpecies
EOF2

    cd $dir
    sbatch run_slurm.sh
    cd ..
done
