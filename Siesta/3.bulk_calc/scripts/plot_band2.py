#!/usr/bin/env python3
"""
밴드 구조 그리기

사용법:
    python /path/to/scripts/plot_band.py Graphene.bands
    python /path/to/scripts/plot_band.py output/Graphene.bands

인자로 지정한 SIESTA .bands 파일을 읽어,
그 파일과 같은 디렉토리에 {label}_band.png 저장.
"""
import sys
import argparse
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def read_bands(path: Path):
    """
    SIESTA .bands 파일 파싱.

    포맷 (SIESTA):
        Ef
        kmin  kmax
        Emin  Emax
        nbands  nspins  nkpts
        k  E1  E2 ... En       (한 k점이 여러 줄로 줄바꿈될 수 있음)
        ...
        ntick
        kpos  'label'          (반복)
    """
    with open(path) as f:
        lines = f.readlines()

    efermi = float(lines[0].split()[0])
    kmin, kmax = map(float, lines[1].split())
    emin, emax = map(float, lines[2].split())
    nbands, nspins, nkpts = map(int, lines[3].split())

    # 고유값 블록: 한 k점당 1(k) + nspins*nbands 개의 수를, 줄바꿈에 상관없이
    # 토큰 스트림으로 읽는다.
    ncols  = 1 + nspins * nbands
    needed = nkpts * ncols
    nums, idx = [], 4
    while len(nums) < needed and idx < len(lines):
        nums.extend(map(float, lines[idx].split()))
        idx += 1

    data    = np.array(nums[:needed]).reshape(nkpts, ncols)
    k_arr   = data[:, 0]
    eig_arr = data[:, 1:].reshape(nkpts, nspins, nbands)

    # 남은 줄: k-tick 개수 + (위치, 레이블)
    tick_k, tick_labels = [], []
    for line in lines[idx:]:
        parts = line.split()
        if len(parts) >= 2:
            try:
                pos = float(parts[0])
            except ValueError:
                continue
            lab = parts[1].strip("'\"").replace("\\Gamma", "Γ")
            if lab in ("G", "Gamma"):
                lab = "Γ"
            tick_k.append(pos)
            tick_labels.append(lab)

    return efermi, k_arr, eig_arr, tick_k, tick_labels


def main():
    ap = argparse.ArgumentParser(description="Plot a SIESTA band structure from a .bands file")
    ap.add_argument("bands", help="SIESTA .bands 파일")
    ap.add_argument("-e", "--emin", type=float, default=None,
                    help="표시할 에너지 최소(eV); 없으면 데이터 범위")
    ap.add_argument("-E", "--emax", type=float, default=None,
                    help="표시할 에너지 최대(eV); 없으면 데이터 범위")
    ap.add_argument("-F", "-f", "--fermi-ref", dest="fermi_ref", action="store_true",
                    help="에너지를 E_F=0 기준으로 (기본: 절대에너지)")
    args = ap.parse_args()

    bands_path = Path(args.bands)
    if not bands_path.is_file():
        print(f"[error] '{bands_path}' 파일을 찾을 수 없습니다.")
        sys.exit(1)

    label = bands_path.stem
    print(f"[read] {bands_path}")

    efermi, k, eig, tick_k, tick_labels = read_bands(bands_path)
    nspins = eig.shape[1]

    off = efermi if args.fermi_ref else 0.0   # -F 면 E_F 기준, 아니면 절대

    fig, ax = plt.subplots(figsize=(5, 6), dpi=150)

    colors = ["C0", "C3"]
    for s in range(nspins):
        for b in range(eig.shape[2]):
            ax.plot(k, eig[:, s, b] - off,
                    color=colors[s], lw=0.8, alpha=0.8)

    ax.axhline(0 if args.fermi_ref else efermi,
               color="gray", lw=0.8, ls="--", label="$E_F$")
    ax.set_xlim(k[0], k[-1])
    ax.set_ylabel("$E - E_F$ (eV)" if args.fermi_ref else "$E$ (eV)")
    ax.set_title(f"{label} band structure")

    if tick_k:
        for tk in tick_k:
            ax.axvline(tk, color="k", lw=0.6)
        ax.set_xticks(tick_k)
        ax.set_xticklabels(tick_labels)

    # y 범위(에너지): -e/-E 또는 데이터 범위 (표시 좌표계 기준)
    yvals = eig - off
    ylo = args.emin if args.emin is not None else yvals.min()
    yhi = args.emax if args.emax is not None else yvals.max()
    ax.set_ylim(ylo, yhi)
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()

    out = bands_path.parent / f"{label.lower()}_band.png"
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[saved] {out}")


if __name__ == "__main__":
    main()
