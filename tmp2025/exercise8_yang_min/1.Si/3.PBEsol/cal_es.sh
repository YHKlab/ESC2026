pw_path=~/workspace/q-e/bin
  
$pw_path/pw.x -in Si_PBEsol.scf.in > Si_PBEsol.scf.out
$pw_path/pw.x -in Si_PBEsol.bands.in > Si_PBEsol.bands.out
$pw_path/bands.x -in pp.in > pp.out
