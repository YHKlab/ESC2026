pw_path=~/workspace/q-e/bin
  
$pw_path/pw.x -in Si_LDA.scf.in > Si_LDA.scf.out
$pw_path/pw.x -in Si_LDA.bands.in > Si_LDA.bands.out
$pw_path/bands.x -in pp.in > pp.out
