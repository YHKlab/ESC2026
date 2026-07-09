#!/usr/bin/env python3
"""
구조 최적화 수렴 그래프

사용법:
    python scripts/plot_convergence.py CH4
    python scripts/plot_convergence.py H2O
    python scripts/plot_convergence.py NH3

.MDE 파일에서 step별 E_KS를 읽어 figures/{label}_convergence.png 저장.
"""
import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

SCRIPTS = Path(__file__).resolve().parent
BASE    = SCRIPTS.parent
FIGURES = BASE / "figures"
FIGURES.mkdir(exist_ok=True)


def read_mde(path: Path):
    steps, energies = [], []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            cols = line.split()
            steps.append(int(cols[0]))
            energies.append(float(cols[2]))   # E_KS (eV)
    return np.array(steps), np.array(energies)


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else "CH4"
    mde = BASE / label / f"{label}.MDE"

    if not mde.exists():
        print(f"[error] {mde} not found. 먼저 계산을 실행하세요.")
        sys.exit(1)

    steps, energies = read_mde(mde)

    fig, ax = plt.subplots(figsize=(6, 4), dpi=150)
    ax.plot(steps, energies, marker="o", ms=3, lw=1.2, color="C0")
    ax.set_xlabel("CG Step")
    ax.set_ylabel("$E_{KS}$ (eV)")
    ax.set_title(f"{label} — structural optimization convergence")
    ax.grid(alpha=0.3)
    fig.tight_layout()

    out = FIGURES / f"{label.lower()}_convergence.png"
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[saved] {out}")


if __name__ == "__main__":
    main()
