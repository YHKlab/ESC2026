#!/usr/bin/env python3
"""
준비(Eig2DOS):
    Eig2DOS -f -s 0.1 -n 2000 Graphene.EIG > Graphene.dos.dat
사용법 예시:
    python /path/to/scripts/plot_dos.py Graphene.dos.dat   # Eig2DOS output
    python /path/to/scripts/plot_dos.py Graphene.DOS       # SIESTA 출력 DOS 파일

그림은 입력 파일과 같은 디렉토리에 {label}_dos.png 로 저장.
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


def read_eig2dos_fermi(path: Path):
    """Eig2DOS .dat 헤더에서 (절대 E_F, shifted여부) 반환.
    헤더 예: '# E_F = -4.2667 eV (NOT shifted)' 또는 '... --> (shifted to ZERO)'."""
    ef, shifted = None, False
    for line in path.read_text().splitlines():
        if not line.startswith("#"):
            break
        if "E_F" in line and "=" in line:
            try:
                ef = float(line.split("=")[1].split()[0])
            except (ValueError, IndexError):
                pass
            shifted = "shifted to ZERO" in line
    return ef, shifted


def main():
    ap = argparse.ArgumentParser(description="Plot total DOS (Eig2DOS output or SIESTA .DOS)")
    ap.add_argument("file", help="Eig2DOS 출력 또는 SIESTA .DOS 파일")
    ap.add_argument("-e", "--emin", type=float, default=None,
                    help="표시할 에너지 최소(eV); 없으면 데이터 범위")
    ap.add_argument("-E", "--emax", type=float, default=None,
                    help="표시할 에너지 최대(eV); 없으면 데이터 범위")
    ap.add_argument("-F", "-f", "--fermi-ref", dest="fermi_ref", action="store_true",
                    help="에너지를 E_F=0 기준으로 (기본: 절대에너지)")
    args = ap.parse_args()

    path = Path(args.file)
    if not path.is_file():
        print(f"[error] '{path}' 파일을 찾을 수 없습니다.")
        sys.exit(1)

    print(f"[read] {path}")
    data = np.loadtxt(path, comments="#")
    if data.ndim != 2 or data.shape[1] < 2:
        print(f"[error] 숫자 컬럼이 부족합니다: shape={data.shape}")
        sys.exit(1)
    E_data = data[:, 0]

    if path.suffix == ".DOS":
        # SIESTA 총 DOS: 절대에너지.  컬럼 = E  DOS [DOS_down]
        if data.shape[1] >= 3:
            n_up, n_dn, ntot = data[:, 1], data[:, 2], data[:, 1] + data[:, 2]
        else:
            n_up = n_dn = ntot = data[:, 1]
        efermi_abs = find_fermi(path.parent)
        E_abs = E_data                                   # 이미 절대
    else:
        # .DOS 가 아니면 Eig2DOS 출력으로 간주.  컬럼 = E N(up) N(down) Ntot
        if data.shape[1] < 4:
            print(f"[error] Eig2DOS 형식(>=4 컬럼)이 아닙니다: shape={data.shape}")
            sys.exit(1)
        n_up, n_dn, ntot = data[:, 1], data[:, 2], data[:, 3]
        ef_hdr, shifted = read_eig2dos_fermi(path)       # 절대 E_F, shift 여부
        efermi_abs = ef_hdr
        a_cur = 0.0 if shifted else (ef_hdr if ef_hdr is not None else 0.0)
        E_abs = E_data + ((ef_hdr - a_cur) if ef_hdr is not None else 0.0)

    # 표시 좌표계: -F 면 E_F=0 기준, 아니면 절대
    off = efermi_abs if (args.fermi_ref and efermi_abs is not None) else 0.0
    E = E_abs - off
    fline = 0.0 if args.fermi_ref else efermi_abs
    xlabel = "$E - E_F$ (eV)" if args.fermi_ref else "$E$ (eV)"

    spin_polarized = not np.allclose(n_up, n_dn)

    label = path.stem
    if label.endswith(".dos"):
        label = label[:-4]

    fig, ax = plt.subplots(figsize=(5, 5), dpi=150)
    ax.plot(E, ntot, color="C0", lw=1.5, label="Total DOS")
    if spin_polarized:
        ax.plot(E,  n_up, color="C3", lw=1.0, ls="--", label="up")
        ax.plot(E, -n_dn, color="C2", lw=1.0, ls="--", label="down")
        ax.axhline(0, color="k", lw=0.6)

    if fline is not None:
        ax.axvline(fline, color="gray", lw=0.8, ls="--", label="$E_F$")
    else:
        print("[info] 페르미 에너지를 못 찾아 E_F 선을 생략합니다 (.DOS 는 *.EIG 필요).")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("DOS (states/eV)")
    ax.set_title(f"{label} DOS")
    xlo = args.emin if args.emin is not None else E[0]
    xhi = args.emax if args.emax is not None else E[-1]
    ax.set_xlim(xlo, xhi)
    if not spin_polarized:
        ax.set_ylim(bottom=0)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.2)
    fig.tight_layout()

    out = path.parent / f"{label.lower()}_dos.png"
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[saved] {out}")


if __name__ == "__main__":
    main()
