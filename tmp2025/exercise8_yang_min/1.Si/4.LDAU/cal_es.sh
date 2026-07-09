pw_path=~/workspace/q-e/bin
  
$pw_path/pw.x -in Si_LDAU.scf.in > Si_LDAU.scf.out
$pw_path/pw.x -in Si_LDAU.bands.in > Si_LDAU.bands.out
$pw_path/bands.x -in pp.in > pp.out
