cd install
git clone -b qe-7.3 https://gitlab.com/QEF/q-e.git
git clone https://github.com/KIAS-CMT/DFT-U-V.git
cd DFT-U-V 
cp qe-7.3_ehub_uv.diff ../q-e/
cd ../q-e
./configure
patch -p1 < qe-7.3_ehub_uv.diff
