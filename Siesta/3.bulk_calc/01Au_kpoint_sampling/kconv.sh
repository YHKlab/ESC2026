
#!/bin/bash
set -e

for k in 5 9 15 21 25 31 35
do
    dir=k${k}
    mkdir -p $dir
    cp RUN.fdf STRUCT.fdf BASIS.fdf Au.psf run_slurm.sh $dir/

    cat > $dir/KPT.fdf << KEOF
%block kgrid_Monkhorst_Pack
$k 0 0 0.0
0 $k 0 0.0
0 0 $k 0.0
%endblock kgrid_Monkhorst_Pack
KEOF

    cd $dir
    sbatch run_slurm.sh
    cd ..
done



