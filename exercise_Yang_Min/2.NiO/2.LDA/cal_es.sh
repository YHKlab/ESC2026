pw_path=~/workspace/q-e/bin
  
$pw_path/pw.x -in NiO_LDA.scf.in > NiO_LDA.scf.out
$pw_path/pw.x -in NiO_LDA.bands.in > NiO_LDA.bands.out
$pw_path/bands.x -in pp.in > pp.out
