# 3. 벌크 계산 실습

세 시스템 × (밴드 / DOS / PDOS). 각 시스템은 `1.band` / `2.DOS` / `3.PDOS` 하위 폴더로
나뉘고, 각 폴더에 제출 스크립트 `slm_siesta_run` 이 있다.

| # | 시스템 | 구조 | SystemLabel |
|---|--------|------|-------------|
| 1 | Graphene | 2D 육방 (반금속) | `Graphene` |
| 2 | GaAs | zinc-blende (반도체) | `GaAs` |
| 3 | MgO | rocksalt (절연체) | `MgO` |

## 준비

```bash
conda activate siesta
cd ~/workspace/ESC2026/Siesta/3.bulk_calc
```
- 슈도포텐셜·기저는 각 `input/` 에 포함.
- 후처리 도구(`gnubands`, `Eig2DOS`, `fmpdos`)는 SIESTA 와 함께 PATH(`/opt/siesta-5.4.2-install/bin`)에 있음.
- 플롯 스크립트는 `scripts/` (출력 파일과 같은 폴더에 `*.png` 저장).

---

## 계산 실행 (공통)

각 하위 폴더(`1.band`, `2.DOS`, `3.PDOS`)에서:
```bash
sbatch slm_siesta_run        # input/ → output/ 복사 후 output/ 에서 실행
squeue -u $USER              # 대기열 확인
tail -f output/stdout.txt    # 진행 로그
grep "Job completed" output/stdout.txt   # 정상 종료 확인
```

후처리는 결과가 있는 `output/` 안에서 실행한다.
플롯 옵션(공통): `-e/-E` 표시 에너지 범위, `-F` E_F=0 기준(기본은 절대에너지).

---

## 1. Graphene

### 밴드
```bash
cd 1.Graphene/1.band && sbatch slm_siesta_run
cd output
gnubands Graphene.bands > Graphene.bands.dat
python ../../../scripts/plot_band.py Graphene.bands.dat -F
```

### DOS
```bash
cd 1.Graphene/2.DOS && sbatch slm_siesta_run
cd output
Eig2DOS Graphene.EIG > Graphene.dos.dat
python ../../../scripts/plot_dos.py Graphene.dos.dat -F
```

### PDOS
```bash
cd 1.Graphene/3.PDOS && sbatch slm_siesta_run
cd output
fmpdos        # Graphene.PDOS 읽고 원소·n,l,m 입력 → 예: C_2pz.pdos
python ../../../scripts/plot_pdos.py C_2pz.pdos -F     # 총 DOS 배경 자동 포함
```

---

## 2. GaAs

### 밴드
```bash
cd 2.GaAs/1.band && sbatch slm_siesta_run
cd output
gnubands GaAs.bands > GaAs.bands.dat
python ../../../scripts/plot_band.py GaAs.bands.dat -F
```

### DOS
```bash
cd 2.GaAs/2.DOS && sbatch slm_siesta_run
cd output
Eig2DOS GaAs.EIG > GaAs.dos.dat
python ../../../scripts/plot_dos.py GaAs.dos.dat -F
```

### PDOS
```bash
cd 2.GaAs/3.PDOS && sbatch slm_siesta_run
cd output
fmpdos        # GaAs.PDOS → 예: Ga_4s.pdos, As_4p.pdos
python ../../../scripts/plot_pdos.py As_4p.pdos -F
```

---

## 3. MgO

### 밴드
```bash
cd 3.MgO/1.band && sbatch slm_siesta_run
cd output
gnubands MgO.bands > MgO.bands.dat
python ../../../scripts/plot_band.py MgO.bands.dat -F
```

### DOS
```bash
cd 3.MgO/2.DOS && sbatch slm_siesta_run
cd output
Eig2DOS MgO.EIG > MgO.dos.dat
python ../../../scripts/plot_dos.py MgO.dos.dat -F
```

### PDOS
```bash
cd 3.MgO/3.PDOS && sbatch slm_siesta_run
cd output
fmpdos        # MgO.PDOS → 예: O_2p.pdos, Mg_3s.pdos
python ../../../scripts/plot_pdos.py O_2p.pdos -F
```

---

## 후처리 도구 ↔ 입력 파일

| 계산 | SIESTA 출력 | 후처리 도구 | 플롯 스크립트 |
|------|-------------|-------------|---------------|
| 밴드 | `*.bands` | `gnubands` → `*.bands.dat` | `plot_band.py` |
| DOS  | `*.EIG`(+`*.KP`) | `Eig2DOS` → `*.dos.dat` | `plot_dos.py` |
| PDOS | `*.PDOS` | `fmpdos` → `*.pdos` (대화식) | `plot_pdos.py` |

> 참고: SIESTA 가 PDOS 계산에서 같이 내놓는 총 DOS `*.DOS`(2열)도 `plot_dos.py` 로 바로 그릴 수 있다.
> 도구 없이 직접 처리하는 `plot_band2.py`(`.bands`) / `plot_dos2.py`(`.EIG`+`.KP`) / `plot_pdos2.py`(`.PDOS`, sisl) 변형도 있다.

## 밴드 경로 (고대칭점)

- **Graphene** (2D 육방): Γ–M–K–Γ
- **GaAs · MgO** (FCC): 예) L–Γ–X–W–K  (정확한 경로는 `input/RUN.fdf` 의 `%block BandLines` 참고)

| 점 | FCC 분수좌표 (b₁,b₂,b₃) |
|----|--------------------------|
| Γ  | (0, 0, 0)   |
| X  | (0, ½, ½)   |
| L  | (½, ½, ½)   |
| W  | (½, ¼, ¾)   |
| K  | (⅜, ⅜, ¾)   |
