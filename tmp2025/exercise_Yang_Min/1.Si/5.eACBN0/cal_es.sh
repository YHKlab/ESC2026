pw_path=~/workspace/q-e/bin
  
$pw_path/pw.x -in Si_eACBN0.scf.in > Si_eACBN0.scf.out
$pw_path/pw.x -in Si_eACBN0.bands.in > Si_eACBN0.bands.out
$pw_path/bands.x -in pp.in > pp.out
