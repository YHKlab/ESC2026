# 3. 벌크 계산 실습

## 준비

```bash
conda activate summer
cd ~/2026-Siesta/3.bulk_calc
```

**슈도포텐셜 (최초 1회)**
```bash
# Pseudo-Dojo NC-SR PBE: https://www.pseudo-dojo.org
wget https://www.pseudo-dojo.org/pseudos/nc-sr-04_pbe_standard_psml.tgz
tar xzf nc-sr-04_pbe_standard_psml.tgz Au.psml Si.psml
cp Au.psml Au/
cp Si.psml Si/
```

---

## Au (FCC 금속)

**계산 실행**
```bash
cd Au
sbatch run.sh
squeue -u $USER
tail -f Au.out
```

**수렴 확인**
```bash
grep "scf" Au.out | tail -20      # SCF 반복
grep "E_KS" Au.out | tail -5      # 총 에너지
```

**구조 보기**
```bash
sgeom STRUCT.fdf STRUCT.xsf       # 초기 구조 → XSF 변환
```

**밴드 구조**
```bash
python scripts/plot_band.py Au    # figures/au_band.png
```

**DOS**
```bash
python scripts/plot_dos.py Au     # figures/au_dos.png
```

---

## Si (diamond 반도체)

**계산 실행**
```bash
cd Si
sbatch run.sh
squeue -u $USER
tail -f Si.out
```

**수렴 확인**
```bash
grep "E_KS" Si.out | tail -5
```

**구조 보기**
```bash
sgeom STRUCT.fdf STRUCT.xsf
```

**밴드 구조**
```bash
python scripts/plot_band.py Si    # figures/si_band.png
```

**DOS**
```bash
python scripts/plot_dos.py Si     # figures/si_dos.png
```

---

## 출력 파일 요약

| 파일 | 내용 |
|------|------|
| `*.out` | 전체 SIESTA 출력 |
| `*.EIG` | SCF k-mesh 고유값 |
| `*.bands` | 밴드 경로 고유값 (plot_band 입력) |
| `*.KP` | SCF k-point 좌표·가중치 |
| `*.PDOS` | 원자·궤도 투영 DOS (plot_dos 입력) |

---

## 참고: FCC BZ 고대칭점 (Au, Si 공통)

| 점 | 분수 좌표 (b₁, b₂, b₃) | Cartesian (2π/a) |
|----|------------------------|-----------------|
| Γ  | (0, 0, 0)              | (0, 0, 0)       |
| L  | (½, ½, ½)              | (½, ½, ½)       |
| X  | (0, ½, ½)              | (1, 0, 0)       |
| W  | (½, ¼, ¾)              | (½, 1, 0)       |
| K  | (⅜, ⅜, ¾)              | (¾, ¾, 0)       |
