#!/usr/bin/env python3
"""
DOS / PDOS 그리기

사용법:
    python scripts/plot_dos.py Au
    python scripts/plot_dos.py Si

SIESTA 출력 {label}.PDOS (XML) 파일을 sisl로 읽어
Total DOS + 원자별 PDOS를 figures/{label}_dos.png 로 저장.
"""
import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

SCRIPTS = Path(__file__).resolve().parent
BASE    = SCRIPTS.parent
FIGURES = BASE / "figures"
FIGURES.mkdir(exist_ok=True)


def main():
    import sisl

    label = sys.argv[1] if len(sys.argv) > 1 else "Au"
    pdos_path = BASE / label / f"{label}.PDOS"

    if not pdos_path.exists():
        print(f"[error] {pdos_path} not found.")
        print("  RUN.fdf 에 ProjectedDensityOfStates 블록이 있어야 합니다.")
        sys.exit(1)

    # sisl로 PDOS 읽기
    pdos_sile = sisl.get_sile(str(pdos_path))
    geometry, E, PDOS = pdos_sile.read_data()
    # PDOS shape: (natoms, norbs_per_atom, nE) or varies by sisl version

    # Total DOS: 전체 합산
    total_dos = PDOS.sum(axis=(0, 1)) if PDOS.ndim == 3 else PDOS.sum(axis=0)

    # Fermi 에너지는 PDOS에 포함된 E 범위의 중심 근처(0 기준)
    # sisl은 E를 이미 Fermi 기준으로 반환하는 경우가 많음
    efermi = 0.0

    fig, ax = plt.subplots(figsize=(5, 5), dpi=150)
    ax.plot(E - efermi, total_dos, color="C0", lw=1.5, label="Total DOS")

    # 원소별 PDOS (간단히 원자별 합산)
    syms = [geometry.atoms[i].symbol for i in range(len(geometry))]
    unique = list(dict.fromkeys(syms))
    colors = ["C1", "C3", "C2", "C4"]
    for idx, sym in enumerate(unique):
        atom_idx = [i for i, s in enumerate(syms) if s == sym]
        if PDOS.ndim == 3:
            pdos_elem = PDOS[atom_idx].sum(axis=(0, 1))
        else:
            pdos_elem = PDOS[atom_idx].sum(axis=0)
        ax.plot(E - efermi, pdos_elem,
                color=colors[idx % len(colors)], lw=1.0,
                ls="--", label=f"{sym} PDOS")

    ax.axvline(0, color="gray", lw=0.8, ls="--", label="$E_F$")
    ax.set_xlabel("$E - E_F$ (eV)")
    ax.set_ylabel("DOS (states/eV)")
    ax.set_title(f"{label} DOS")
    ax.set_xlim(E[0] - efermi, E[-1] - efermi)
    ax.set_ylim(bottom=0)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.2)
    fig.tight_layout()

    out = FIGURES / f"{label.lower()}_dos.png"
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[saved] {out}")


if __name__ == "__main__":
    main()
