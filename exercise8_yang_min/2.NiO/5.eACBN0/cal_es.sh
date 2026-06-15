pw_path=~/workspace/q-e/bin
  
$pw_path/pw.x -in NiO_eACBN0.scf.in > NiO_eACBN0.scf.out
$pw_path/pw.x -in NiO_eACBN0.bands.in > NiO_eACBN0.bands.out
$pw_path/bands.x -in pp.in > pp.out
