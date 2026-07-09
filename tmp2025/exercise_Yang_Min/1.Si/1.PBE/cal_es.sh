pw_path=~/workspace/q-e/bin
  
$pw_path/pw.x -in Si_PBE.scf.in > Si_PBE.scf.out
$pw_path/pw.x -in Si_PBE.bands.in > Si_PBE.bands.out
$pw_path/bands.x -in pp.in > pp.out
