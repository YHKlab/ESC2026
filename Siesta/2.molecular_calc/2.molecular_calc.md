# 2. 분자 계산 실습

## 준비

```bash
conda activate summer
cd ~/2026-Siesta/2.molecular_calc
```

---

## CH4 — 구조 최적화 + basis 수렴성

**계산 실행**
```bash
cd CH4
sbatch run.sh
squeue -u $USER          # 잡 상태 확인
tail -f CH4.out          # 실시간 출력
```

**수렴 확인**
```bash
grep "SCF cycle" CH4.out         # SCF 반복 수
grep "E_KS" CH4.out              # 총 에너지 추이
python scripts/plot_convergence.py CH4   # figures/ch4_convergence.png
```

**구조 보기**
```bash
sgeom STRUCT.fdf CH4_initial.xsf     # 초기 구조 → XSF 변환
sgeom CH4.XV    CH4_opt.xsf     # 최적화 후 구조 → XSF 변환
```

**Basis 수렴성 (SZ / DZ / TZ / DZP)**
```bash
for d in SZ DZ TZ DZP; do
    cd CH4_basis_sweep/$d && sbatch run.sh && cd ../..
done
# 계산 완료 후
python scripts/basis_convergence.py    # figures/ch4_basis_convergence.png
```

---

## H2O — 구조 최적화 + 전하 밀도

> `H2O/RUN.fdf` 에 `SaveRho T`, `SaveDeltaRho T` 가 켜져 있어야 함

**계산 실행**
```bash
cd H2O
sbatch run.sh
```

**수렴 확인**
```bash
python scripts/plot_convergence.py H2O   # figures/h2o_convergence.png
```

**구조 보기**
```bash
sgeom STRUCT.fdf STRUCT.xsf     # 초기 구조 → XSF 변환
sgeom H2O.XV    H2O_opt.xsf     # 최적화 후 구조 → XSF 변환
```

**전하 밀도 시각화**
```bash
python scripts/plot_rho_slice.py H2O
# → figures/h2o_rho_slice.png   (전체 전하 밀도)
# → figures/h2o_drho_slice.png  (차분 전하 밀도)
```

**Hirshfeld 부분 전하 확인**
```bash
grep -A 10 "Hirshfeld" H2O.out
```

---

## NH3 — 직접 해보기

**체크리스트**
1. `NH3/STRUCT.fdf` 에서 원자 하나의 좌표를 약간 바꿔 비대칭 초기 구조 만들기
2. 계산 실행 후 N-H ≈ 1.01 Å, H-N-H ≈ 107° 로 수렴하는지 확인
3. `BASIS.fdf` 에서 `PAO.BasisSize` 바꿔 basis 수렴성 비교
4. `RUN.fdf` 에 `SaveRho T` 추가 후 전하 밀도 시각화

```bash
cd NH3
sbatch run.sh
python scripts/plot_convergence.py NH3
sgeom STRUCT.fdf STRUCT.xsf     # 초기 구조 → XSF 변환
sgeom NH3.XV    NH3_opt.xsf     # 최적화 후 구조 → XSF 변환
python scripts/plot_rho_slice.py NH3
```

---

## 출력 파일 요약

| 파일 | 내용 |
|------|------|
| `*.out` | 전체 SIESTA 출력 (에너지, SCF) |
| `*.XV` | 최적화 후 최종 구조 |
| `*.ANI` | 전체 최적화 궤적 (xyz) |
| `*.MDE` | step별 에너지·온도·압력 |
| `*.RHO` | 전체 전자 밀도 |
| `*.DRHO` | 차분 전자 밀도 (SCF - 자유원자) |
