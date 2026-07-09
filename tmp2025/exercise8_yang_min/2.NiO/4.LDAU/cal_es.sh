pw_path=~/workspace/q-e/bin
  
$pw_path/pw.x -in NiO_LDAU.scf.in > NiO_LDAU.scf.out
$pw_path/pw.x -in NiO_LDAU.bands.in > NiO_LDAU.bands.out
$pw_path/bands.x -in pp.in > pp.out
