pw_path=~/workspace/q-e/bin
  
$pw_path/pw.x -in NiO_PBE.scf.in > NiO_PBE.scf.out
$pw_path/pw.x -in NiO_PBE.bands.in > NiO_PBE.bands.out
$pw_path/bands.x -in pp.in > pp.out
