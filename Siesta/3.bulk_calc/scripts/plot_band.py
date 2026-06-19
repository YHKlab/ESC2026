#!/usr/bin/env python3
"""
밴드 구조 그리기

사용법:
    python scripts/plot_band.py Au
    python scripts/plot_band.py Si

SIESTA 출력 {label}.bands 파일을 읽어
figures/{label}_band.png 저장.
"""
import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

SCRIPTS = Path(__file__).resolve().parent
BASE    = SCRIPTS.parent
FIGURES = BASE / "figures"
FIGURES.mkdir(exist_ok=True)


def read_bands(path: Path):
    """
    SIESTA .bands 파일 파싱.

    포맷:
        Ef
        kmin  kmax
        nbands  nspins  nkpts
        k  E1  E2 ... En       (반복)
        ...
        label_line (tic positions + labels)
    """
    with open(path) as f:
        lines = f.readlines()

    efermi = float(lines[0].split()[0])
    kmin, kmax = map(float, lines[1].split())
    nbands, nspins, nkpts = map(int, lines[2].split())

    k_arr   = np.zeros(nkpts)
    eig_arr = np.zeros((nkpts, nspins, nbands))

    for i in range(nkpts):
        vals = list(map(float, lines[3 + i].split()))
        k_arr[i] = vals[0]
        eig_arr[i] = np.array(vals[1:]).reshape(nspins, nbands)

    # 마지막 블록: k-tick 위치 + 레이블
    tick_k, tick_labels = [], []
    for line in lines[3 + nkpts:]:
        parts = line.split()
        if len(parts) >= 2:
            try:
                tick_k.append(float(parts[0]))
                tick_labels.append(parts[1].replace("\\Gamma", "Γ"))
            except ValueError:
                pass

    return efermi, k_arr, eig_arr, tick_k, tick_labels


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else "Au"
    bands_path = BASE / label / f"{label}.bands"

    if not bands_path.exists():
        print(f"[error] {bands_path} not found. 먼저 계산을 실행하세요.")
        sys.exit(1)

    efermi, k, eig, tick_k, tick_labels = read_bands(bands_path)
    nspins = eig.shape[1]

    fig, ax = plt.subplots(figsize=(5, 6), dpi=150)

    colors = ["C0", "C3"]
    for s in range(nspins):
        for b in range(eig.shape[2]):
            ax.plot(k, eig[:, s, b] - efermi,
                    color=colors[s], lw=0.8, alpha=0.8)

    ax.axhline(0, color="gray", lw=0.8, ls="--", label="$E_F$")
    ax.set_xlim(k[0], k[-1])
    ax.set_ylabel("$E - E_F$ (eV)")
    ax.set_title(f"{label} band structure")

    if tick_k:
        for tk in tick_k:
            ax.axvline(tk, color="k", lw=0.6)
        ax.set_xticks(tick_k)
        ax.set_xticklabels(tick_labels)

    # y 범위: Fermi 기준 ±5 eV (금속) 또는 자동
    ax.set_ylim(-8, 6)
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()

    out = FIGURES / f"{label.lower()}_band.png"
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[saved] {out}")


if __name__ == "__main__":
    main()
