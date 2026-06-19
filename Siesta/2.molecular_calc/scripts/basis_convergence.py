#!/usr/bin/env python3
"""
CH4 basis 수렴성 분석

사용법:
    python scripts/basis_convergence.py

CH4_basis_sweep/{SZ,DZ,TZ,DZP}/ 의 CH4.XV, CH4.out 을 읽어
결합 길이·총 에너지 수렴 그래프를 figures/ch4_basis_convergence.png 로 저장.
"""
import re
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from ase.io import read

SCRIPTS = Path(__file__).resolve().parent
BASE    = SCRIPTS.parent
SWEEP   = BASE / "CH4_basis_sweep"
FIGURES = BASE / "figures"
FIGURES.mkdir(exist_ok=True)

BASES   = ["SZ", "DZ", "TZ", "DZP"]
REF_BOND = 1.087   # Å (Handy et al. 1993)


def read_bonds(xv_path: Path):
    atoms = read(str(xv_path))
    pos = atoms.get_positions()
    syms = atoms.get_chemical_symbols()
    c = pos[syms.index("C")]
    h_pos = [pos[i] for i, s in enumerate(syms) if s == "H"]
    return [np.linalg.norm(h - c) for h in h_pos]


def read_etot(out_path: Path):
    pat = re.compile(r"siesta:\s+E_KS\(eV\)\s*=\s*(-?\d+\.\d+)")
    last = None
    with open(out_path) as f:
        for line in f:
            m = pat.search(line)
            if m:
                last = float(m.group(1))
    return last


def main():
    rows = []
    for basis in BASES:
        xv  = SWEEP / basis / "CH4.XV"
        out = SWEEP / basis / "CH4.out"
        if not xv.exists():
            print(f"[skip] {basis}: {xv} not found")
            continue
        bonds = read_bonds(xv)
        etot  = read_etot(out) if out.exists() else None
        rows.append({"basis": basis,
                     "bond": np.mean(bonds),
                     "etot": etot})
        print(f"{basis}: bond={np.mean(bonds):.4f} Å  E={etot} eV")

    if not rows:
        print("[error] 결과 없음. 먼저 basis sweep 계산을 실행하세요.")
        return

    labels = [r["basis"] for r in rows]
    xs     = np.arange(len(rows))
    bonds  = [r["bond"] for r in rows]
    etots  = [r["etot"] for r in rows]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4), dpi=150)

    ax1.plot(xs, bonds, marker="o", color="C0")
    ax1.axhline(REF_BOND, ls="--", color="gray", label=f"Reference {REF_BOND} Å")
    ax1.set_xticks(xs); ax1.set_xticklabels(labels)
    ax1.set_xlabel("Basis"); ax1.set_ylabel("C-H bond length (Å)")
    ax1.set_title("CH$_4$ bond length convergence")
    ax1.legend(fontsize=8); ax1.grid(alpha=0.3)

    valid = [(i, e) for i, e in enumerate(etots) if e is not None]
    if valid:
        e_ref = valid[-1][1]
        idxs, de = zip(*[(i, (e - e_ref) * 1e3) for i, e in valid])
        ax2.plot(list(idxs), list(de), marker="s", color="C3")
        ax2.axhline(0, ls="--", color="gray", alpha=0.6)
        ax2.set_xticks(xs); ax2.set_xticklabels(labels)
        ax2.set_xlabel("Basis"); ax2.set_ylabel("$E - E_{DZP}$ (meV)")
        ax2.set_title("CH$_4$ total energy convergence")
        ax2.grid(alpha=0.3)

    fig.tight_layout()
    out = FIGURES / "ch4_basis_convergence.png"
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[saved] {out}")


if __name__ == "__main__":
    main()
