# QE bin 경로: setup_env.sh가 export한 QE_BIN 사용
# (미설정 시 프로젝트 로컬 빌드 경로로 자동 폴백)
if [ -z "${QE_BIN:-}" ]; then
    _here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    _root="$(cd "$_here/../.." && pwd)"   # exe4-DFT_UV
    QE_BIN="$_root/qe73_build/q-e/bin"
fi
pw_path="$QE_BIN"
  
$pw_path/pw.x -in Si_eACBN0.scf.in > Si_eACBN0.scf.out
$pw_path/pw.x -in Si_eACBN0.bands.in > Si_eACBN0.bands.out
$pw_path/bands.x -in pp.in > pp.out
