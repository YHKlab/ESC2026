pw_path=~/workspace/q-e/bin
  
$pw_path/pw.x -in NiO_PBEsol.scf.in > NiO_PBEsol.scf.out
$pw_path/pw.x -in NiO_PBEsol.bands.in > NiO_PBEsol.bands.out
$pw_path/bands.x -in pp.in > pp.out
