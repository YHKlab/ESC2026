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
pip install qe irrep ray wannierberri
```

---
**주의: 이번 계산은 편의를 위해 아직 수렴이 안된 parameter를 사용했기 때문에 실제 계산에서는 반드시 수렴 test를 해봐야 한다.**

## 1. DFT 계산

### 1.1 개요

Wannier interpolation을 하기 위해선 우선 SCF 계산을 한 다음에, coarse *ab initio* grid에서 NSCF 계산을 진행해야 한다. 이 과정에서 추후 비교를 위해 k-point path를 따라 band 구조도 계산한다.

### 1.2 실행

```bash
cd DFT
bash run_scf.sh
```

---

## 2. Wannierization

### 2.1 개요

이전 단계에서 진행한 NSCF 계산을 바탕으로 Wannierization과 Wannier interpolation에 필요한 파일들 (.amn, .mmn, .eig, .uHu)를 생성하고, Wannier90을 이용해 Wannierization을 진행한다.

### 2.2 실행

```bash
cd ../W90
bash run_w90.sh
```

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
