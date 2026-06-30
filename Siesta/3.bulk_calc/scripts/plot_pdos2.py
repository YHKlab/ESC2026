#!/usr/bin/env python3
"""
DOS / PDOS 그리기

사용법:
    python /path/to/scripts/plot_dos.py Graphene.PDOS
    python /path/to/scripts/plot_dos.py output/Graphene.PDOS

인자로 지정한 SIESTA {label}.PDOS (XML) 파일을 sisl로 읽어,
그 파일과 같은 디렉토리에 Total DOS + 원소별 PDOS를 {label}_dos.png 로 저장.
"""
import sys
import argparse
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def find_fermi(folder: Path):
    """폴더의 *.EIG 첫 줄에서 페르미 에너지(eV, 절대값)를 읽는다."""
    eigs = sorted(folder.glob("*.EIG"))
    if not eigs:
        return None
    try:
        with open(eigs[0]) as f:
            ef = float(f.readline().split()[0])
        print(f"[read] {eigs[0]}  (E_F = {ef:.4f} eV)")
        return ef
    except (ValueError, IndexError):
        return None


def main():
    import sisl

    ap = argparse.ArgumentParser(description="Plot total + per-element PDOS from a SIESTA .PDOS (sisl)")
    ap.add_argument("pdos", help="SIESTA .PDOS 파일")
    ap.add_argument("-e", "--emin", type=float, default=None,
                    help="표시할 에너지 최소(eV); 없으면 데이터 범위")
    ap.add_argument("-E", "--emax", type=float, default=None,
                    help="표시할 에너지 최대(eV); 없으면 데이터 범위")
    ap.add_argument("-F", "-f", "--fermi-ref", dest="fermi_ref", action="store_true",
                    help="에너지를 E_F=0 기준으로 (기본: 절대에너지)")
    args = ap.parse_args()

    pdos_path = Path(args.pdos)
    if not pdos_path.is_file():
        print(f"[error] '{pdos_path}' 파일을 찾을 수 없습니다.")
        print("  RUN.fdf 에 ProjectedDensityOfStates 블록이 있어야 .PDOS 가 생성됩니다.")
        sys.exit(1)

    label = pdos_path.stem
    print(f"[read] {pdos_path}")

    # sisl로 PDOS 읽기
    pdos_sile = sisl.get_sile(str(pdos_path))
    geometry, E, PDOS = pdos_sile.read_data()
    # PDOS shape: (nspin, norbitals, nE)  ← 궤도 단위 (sisl 0.16 기준).
    # E 는 이미 Fermi 기준(E_F = 0)으로 반환됨.

    # Total DOS: 모든 spin·궤도 합산 → (nE,)
    total_dos = PDOS.sum(axis=(0, 1)) if PDOS.ndim == 3 else PDOS.sum(axis=0)

    # sisl E 는 Fermi 기준(E_F=0). 절대로 변환하려면 *.EIG 의 절대 E_F 필요.
    efermi_abs = find_fermi(pdos_path.parent)
    if efermi_abs is None and not args.fermi_ref:
        print("[info] *.EIG 없음 → 절대에너지 변환 불가, E_F 기준으로 그립니다.")
    fermi_ref = args.fermi_ref or (efermi_abs is None)
    if fermi_ref:
        Edisp = E                      # 이미 Fermi 기준
        fline = 0.0
        xlabel = "$E - E_F$ (eV)"
    else:
        Edisp = E + efermi_abs         # 절대에너지로 변환
        fline = efermi_abs
        xlabel = "$E$ (eV)"

    fig, ax = plt.subplots(figsize=(5, 5), dpi=150)
    ax.plot(Edisp, total_dos, color="C0", lw=1.5, label="Total DOS")

    # 원소별 PDOS: 궤도를 원자(→원소)로 매핑해 합산.
    # geometry.firsto[a]:firsto[a+1] = 원자 a 가 가진 궤도 인덱스 범위.
    syms   = [geometry.atoms[i].symbol for i in range(geometry.na)]
    firsto = geometry.firsto
    unique = list(dict.fromkeys(syms))
    colors = ["C1", "C3", "C2", "C4"]
    for idx, sym in enumerate(unique):
        atom_idx = [i for i, s in enumerate(syms) if s == sym]
        orb_idx  = np.concatenate(
            [np.arange(firsto[a], firsto[a + 1]) for a in atom_idx])
        if PDOS.ndim == 3:
            pdos_elem = PDOS[:, orb_idx, :].sum(axis=(0, 1))
        else:
            pdos_elem = PDOS[orb_idx].sum(axis=0)
        ax.plot(Edisp, pdos_elem,
                color=colors[idx % len(colors)], lw=1.0,
                ls="--", label=f"{sym} PDOS")

    ax.axvline(fline, color="gray", lw=0.8, ls="--", label="$E_F$")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("DOS (states/eV)")
    ax.set_title(f"{label} DOS")
    xlo = args.emin if args.emin is not None else Edisp[0]
    xhi = args.emax if args.emax is not None else Edisp[-1]
    ax.set_xlim(xlo, xhi)
    ax.set_ylim(bottom=0)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.2)
    fig.tight_layout()

    out = pdos_path.parent / f"{label.lower()}_dos.png"
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[saved] {out}")


if __name__ == "__main__":
    main()
