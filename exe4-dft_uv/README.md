# 실습 4: DFT+U+V (eACBN0)

Si와 NiO를 여러 교환상관 범함수(PBE / LDA / PBEsol / LDA+U / eACBN0 / HSE)로
계산하고, band 구조를 비교합니다. eACBN0가 DFT+U+V에 해당합니다.

## 1. 설치 (최초 1회, 20~40분)

```bash
cd install_QE7.3
bash install_all.sh
```

**$HOME을 건드리지 않습니다.** 모든 것이 이 폴더 안에 설치됩니다:
- miniconda  → `.local/miniconda3/`
- conda 환경 → `.local/env/`
- QE 7.3 + patch → `qe73_build/q-e/`

## 2. 환경 활성화 (계산할 때마다)

```bash
cd exe4-DFT_UV      # 이 폴더
source setup_env.sh
```

`QE_BIN`과 `gnuplot`이 잡힙니다.

## 3. 계산 실행

```bash
cd 1.Si/1.PBE
bash cal_es.sh       # scf → bands → bands.x
```

각 방법론 폴더(`1.PBE` ~ `6.HSE`)에서 동일하게 실행합니다.
NiO도 마찬가지 (`2.NiO/`).

## 4. Band 그리기

각 폴더의 `*_pband.gnu`로 개별 밴드를, 물질 폴더의 `*.multiplot.gnu`로
여러 방법론을 겹쳐 그립니다.

```bash
gnuplot PBE_pband.gnu        # 개별
cd .. && gnuplot si.multiplot.gnu   # 비교
```

> **주의**: `.gnu` 파일의 `E_f1`, `E_f2`... 는 Fermi energy 하드코딩 값입니다.
> 직접 계산한 결과로 그리려면 `*.scf.out`의 Fermi energy를 확인해 수정하세요.
> ```bash
> grep "the Fermi energy" Si_PBE.scf.out
> ```

## 폴더 구조

```
exe4-DFT_UV/
├── install_QE7.3/install_all.sh   설치 스크립트
├── setup_env.sh                   (설치 후 생성) 환경 활성화
├── 1.Si/     Si  6개 방법론
├── 2.NiO/    NiO 5개 방법론
├── pp/       pseudopotential
└── reference_patch_examples/  DFT-U-V patch 공식 예제 (참고용)
```
