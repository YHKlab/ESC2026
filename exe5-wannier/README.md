# Wannier Berri 실습 가이드

이 문서는 EDISON 여름학교 실습에서 Quantum ESPRESSO(QE) / Wannier90(W90) / WannierBerri(WB)로 **DFT 계산 → Wannierization → Wannier Interpolation**를 수행하는 과정을 정리한 가이드입니다.

- **DFT**: bcc Fe의 SCF/NSCF 계산 및 band 구조를 계산합니다.
- **W90**: Wannier90 계산을 위한 파일들을 생성하고, Wannier90로 Wannierization을 합니다.
- **WB**: WannierBerri를 이용해 band 구조, Berry curvature, anomalous Hall conductivity(AHC)와 orbital magnetization의 Wannier Interpolation을 합니다. 

---

## 프로젝트 구조

```text
exe5-wannier/
├── README.md                ← 지금 보고 있는 문서
├── DFT/                     ← DFT 계산
│   ├── pseudo/              ← Fe pseudopotential
│   ├── run_dft.sh           ← DFT 계산 실행
│   ├── Fe.scf.in            ← Fe SCF 계산
│   ├── Fe.band.in           ← Fe band 구조 계산
│   ├── Fe.bands.in          ← Fe band 구조 추출
│   └── Fe.nscf.in           ← Fe coarse grid NSCF 계산
│
├── W90/                     ← Wannierization
│   ├── Fe.pw2wan.in         ← W90 계산을 위한 파일 생성
│   └── Fe.win               ← W90 계산 input
│
├── WB/                      ← Wannier Interpolation
│   └── run_wb.ipynb         ← WB 계산용 Jupyter notebook
```

---

## 0. 사전 준비

### 0.1 실습 자료 다운로드

```bash
git clone https://github.com/YHKlab/ESEC2026.git
cd ESEC2026/exe5-wannier
```

### 0.2 QE / W90 / WB 설치 (Conda 방식)

Conda로 Quantum ESPRESSO/W90/WB를 설치합니다.

```bash
conda create -n wannierberri
conda activate wannierberri
conda install -c conda-forge qe ray irrep wannierberri
```

---
**주의: 이번 계산은 편의를 위해 아직 수렴이 안된 parameter를 사용했기 때문에 실제 계산에서는 반드시 수렴 test를 해봐야 한다.**

## 1. DFT 계산

### 1.1 개요

Wannier interpolation을 하기 위해선 우선 SCF 계산을 한 다음에, coarse *ab initio* grid에서 NSCF 계산을 진행해야 한다. 이 과정에서 추후 비교를 위해 k-point path를 따라 band 구조도 계산한다.

### 1.2 실행

```bash
cd DFT
bash run_dft.sh
python plot_band.py
```

### 1.3 결과 분석

Fe_band.svg에서 band 구조를 보면 -70 eV 와 -35 eV 근처에 flat한 band들이 보인다. 이는 우리가 사용한 Fe pseudopotential에 포함된 $3s$, $3p$ semi-core state에 해당한다. 아래 Fe.upf 파일을 보면 valence electron에 해당하는 nv의 값이 4인데, 이는 아래의 electronic configuration은 아래 4줄을 valence electron으로 보고 pseudopotential을 만들겠다는 뜻이다. 따라서 이 pseudopotential에는 $3s$, $3p$, $3d$, $4s$ state가 들어가 있다.

```
# ATOM AND REFERENCE CONFIGURATION
# atsym  z   nc   nv     iexc    psfile
  Fe 26.00    3    4       3      upf
#
#   n    l    f        energy (Ha)
    1    0    2.00
    2    0    2.00
    2    1    6.00
    3    0    2.00
    3    1    6.00
    3    2    6.00
    4    0    2.00
```

한편 Fe_band_fermi.svg에서 band 구조를 보면 예상대로 Fermi surface가 존재하는 metallic state가 나온 것을 알 수 있다. 이 Fermi level 근처에 섞여 있는 band들이 우리가 관심을 가지고 있는 $3d$와 $4s$가 섞인 band들 이다.


---

## 2. Wannierization

### 2.1 개요

이전 단계에서 진행한 NSCF 계산을 바탕으로 Wannierization과 Wannier interpolation에 필요한 파일들 (.amn, .mmn, .eig, .uHu)를 생성하고, Wannier90을 이용해 Wannierization을 진행한다.

### 2.2 Input 파일 설명

Wannierization에서 제일 중요한 것은 disentanglement의 사용 여부, initial projection과 energy window를 결정하는 것이다. 이를 잘 설정해야 Wannierization이 잘 수렴할 수 있다.

관심이 있는 band들이 다른 band들과 Brillouin zone에서 에너지적으로 완벽히 분리되어 있다면, disentanglement를 사용할 필요가 없다. 대표적인 예시로 FCC diamond나 silicon에서 valence band만 볼 생각이면 disentanglement가 필요 없다. BCC Fe의 경우 Fermi level 근처의 band들이 high energy band들과 엉켜있기 때문에 disentanglement를 사용해야 한다.

한편, 앞선 계산에서 아래에 semi-core band 8개가 있음을 확인하였다. 이 band들은 우리에 관심 밖이기 때문에, 앞으로의 계산에서 이를 제외하는 것이 계산에 편리하다. 이를 위해서 Fe.win에 `exclude_bands = 1-8` parameter를 추가하였다.

그 다음으로는 energy window와 initial proojection을 정해야 한다. Energy window에는 outer window와 inner window가 있는데, 보통 inner window를 정하고, outer window는 default로 두어도 큰 상관이 없다. Inner window는 Wannier interpolation이 잘 작동하는 에너지 영역을 정하는 것이기 때문에, 우리가 관심있어 하는 band들이 충분히 포함되도록 해야 한다. 우리 계산에서는 Fermi level 근처를 볼 것이기 때문에, Fermi level보다 조금 더 위의 에너지는 inner window의 maximum으로 잡으면 된다.

마지막으로 initial projection의 경우, 우리가 관심 있어하는 band가 $3d$와 $4s$ character를 가지고 있으므로, $s$ 오비탈과 $d$ 오비탈을 넣으면 된다. 그러나 실제로 이렇게만 가지고 계산을 하면 그리 좋은 결과가 나오지는 않는다. 실제로는 $p$ 오비탈을 추가하고, cubic symmetry에 맞춰서 $t_{2g}$ 오비탈과 $sp^3d^2$ 혼성 오비탈을 사용해야 Wannierization이 잘 된다. 이 때문에 앞의 NSCF 계산에서도 계산하는 band 개수를 40개로 늘린 것이다.

마지막으로 우리 계산에선 disentanglement만 하고, maximal localization은 진행하지 않는다. 이는 maximal localization이 symmetry를 깨기 때문으로, symmetry를 따지고 싶은 상황에서는 maximal localization을 사용하면 안된다. 만약 maximal localization을 사용하고 싶으면 symmetry-adapted Wannier function (SAWF)를 사용해야 한다.

### 2.3 실행

```bash
cd ../W90
bash run_w90.sh
```

### 2.4 결과 분석

Fe.wout 파일의 마지막 부분을 보면 아래와 같다.

```
 ------------------------------------------------------------------------------
 Final State
  WF centre and spread    1  ( -0.549795,  0.002882,  0.000294 )     0.92854528
  WF centre and spread    2  ( -0.641015,  0.065533, -0.001384 )     0.93742438
  WF centre and spread    3  (  0.550045,  0.003560,  0.000289 )     0.92851982
  WF centre and spread    4  (  0.639585, -0.072340,  0.001053 )     0.93435130
  WF centre and spread    5  ( -0.003062, -0.552741,  0.000282 )     0.92976162
  WF centre and spread    6  (  0.052113, -0.629424,  0.000880 )     0.93086822
  WF centre and spread    7  ( -0.002510,  0.547905,  0.000286 )     0.92726455
  WF centre and spread    8  ( -0.050716,  0.631458, -0.001731 )     0.93527653
  WF centre and spread    9  (  0.000413,  0.002169, -0.472484 )     0.92244155
  WF centre and spread   10  (  0.000402, -0.000297, -0.517588 )     0.93849253
  WF centre and spread   11  (  0.000411,  0.002170,  0.472486 )     0.92244354
  WF centre and spread   12  (  0.001046, -0.003341,  0.517714 )     0.93843400
  WF centre and spread   13  (  0.000067,  0.000145, -0.000000 )     0.44257068
  WF centre and spread   14  (  0.000114, -0.000165,  0.000000 )     0.47119629
  WF centre and spread   15  ( -0.000034, -0.000076,  0.000000 )     0.44255275
  WF centre and spread   16  (  0.000120, -0.000051,  0.000000 )     0.47119848
  WF centre and spread   17  ( -0.000049, -0.000069, -0.000000 )     0.44409136
  WF centre and spread   18  (  0.000094,  0.000038, -0.000000 )     0.47219134
  Sum of centres and spreads ( -0.002770, -0.002646,  0.000097 )    13.91762422

         Spreads (Ang^2)       Omega I      =     6.869858178
        ================       Omega D      =     0.299864202
                               Omega OD     =     6.747901843
    Final Spread (Ang^2)       Omega Total  =    13.917624222
 ------------------------------------------------------------------------------
```

추후 계산을 위해 coarse grid를 너무 성글게 잡아서 결과가 그렇게 정확하지는 않다. Wannierization이 잘 되었는지 확인하는 간단한 방법으로 Wannier function의 spread를 확인하는 방법이 있다. 대략 spread의 값이 1-2 정도거나 이보다 작으면 괜찮으며, 이보다 값이 크면 계산이 잘 안되었을 가능성이 있다. 좀 더 제대로된 방법으로는 뒤에서 해볼 band interpolation을 해보는 것이 있다.

계산이 잘 안 되었을 때는 energy window, initial projection, NSCF 계산의 band 개수를 바꿔보면서 테스트를 해보면 된다.

---

## 3. Wannier Interpolation

### 3.1 개요

Wannierization 결과를 바탕으로 fine interpolation grid에서 다양한 물리량들을 계산한다.

### 3.2 실행

```bash
cd ../WB
ln -sf ../DFT/Fe.bands.dat.gnu
ln -sf ../W90/Fe.mmn
ln -sf ../W90/Fe.chk
ln -sf ../W90/Fe.eig
ln -sf ../W90/Fe.uHu
```
이후 `run_wb.ipynb` 파일에서 계산을 진행하면 된다.

### 3.3 결과 분석

Band interpolation 결과를 보면 coarse grid가 너무 성글기 때문에 그렇게 interpolation이 정확하지는 않은 것을 볼 수 있다. 실제 계산에서는 inner energy window내에서 band interpolation이 잘 되었는지 확인해야 한다.

Wannier interpolation에서 중요한 convergence parameter는 coarse grid이다. 실제 계산에는 coarse grid를 바꿔가면서 우리가 계산한 물리량이 잘 수렴하는지를 확인해야 한다.
