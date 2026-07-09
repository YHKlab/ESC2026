#!/usr/bin/env python3
"""
PDOS 그리기 (SIESTA 후처리 도구 fmpdos 출력 .pdos 를 읽어 그리기)

먼저 fmpdos 로 원하는 원소·궤도(n,l,m,z)를 골라 .pdos 파일을 만든 뒤,
그 결과를 이 스크립트로 그린다. (projection 계산은 fmpdos, 그리기만 여기서)

기본 동작:
    인자로 준 .pdos 곡선과 함께, 같은 폴더의 SIESTA 총 DOS({label}.DOS)를
    자동으로 찾아 회색 배경으로 같이 그린다. (끄려면 --no-total)

준비(인터랙티브):
    fmpdos            # Graphene.PDOS, 원소/원자/n,l,m,z, 에너지 범위 입력 -> C_2pz.pdos
사용법:
    python /path/to/scripts/plot_pdos.py C_2pz.pdos
    python /path/to/scripts/plot_pdos.py C_2pz.pdos C_2px.pdos C_2s.pdos
    python /path/to/scripts/plot_pdos.py C_2pz.pdos --no-total
    python /path/to/scripts/plot_pdos.py C_2pz.pdos --dos Graphene.DOS

컬럼: fmpdos .pdos -> Energy PDOS [PDOS_down],  SIESTA .DOS -> Energy DOS [DOS_down].
Energy 는 절대에너지(eV). 페르미 에너지는 같은 폴더의 *.EIG 첫 줄에서 읽어 세로선으로 표시.
그림은 첫 입력 파일과 같은 디렉토리에 저장(단일: {stem}_pdos.png / 다중: pdos_compare.png).
"""
import sys
import argparse
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def load_two_col(path: Path):
    """E, up, down 반환.  컬럼이 2개면 비자성(down=None)."""
    data = np.loadtxt(path, comments="#")
    if data.ndim != 2 or data.shape[1] < 2:
        raise ValueError(f"예상한 형식이 아닙니다(>=2 컬럼): {path} shape={data.shape}")
    E = data[:, 0]
    if data.shape[1] >= 3:
        return E, data[:, 1], data[:, 2]
    return E, data[:, 1], None


def find_total_dos(folder: Path):
    """폴더에서 SIESTA 총 DOS 파일(*.DOS)을 찾는다."""
    cands = sorted(folder.glob("*.DOS"))
    if not cands:
        return None
    if len(cands) > 1:
        print(f"[warn] .DOS 파일이 여러 개라 첫 번째 사용: {cands[0].name} "
              f"(나머지: {', '.join(p.name for p in cands[1:])})")
    return cands[0]


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
    ap = argparse.ArgumentParser(description="Plot fmpdos .pdos curves with SIESTA total DOS")
    ap.add_argument("pdos", nargs="+", help="fmpdos .pdos 파일 (여러 개 가능)")
    ap.add_argument("--dos", help="총 DOS(.DOS) 파일 (기본: 같은 폴더에서 자동 탐색)")
    ap.add_argument("--no-total", action="store_true", help="총 DOS 배경 끄기")
    ap.add_argument("--fermi", type=float,
                    help="페르미 에너지(eV) 세로선 위치 (기본: 같은 폴더 *.EIG 에서 자동)")
    ap.add_argument("-e", "--emin", type=float, default=None,
                    help="표시할 에너지 최소(eV); 없으면 데이터 범위")
    ap.add_argument("-E", "--emax", type=float, default=None,
                    help="표시할 에너지 최대(eV); 없으면 데이터 범위")
    ap.add_argument("-F", "-f", "--fermi-ref", dest="fermi_ref", action="store_true",
                    help="에너지를 E_F=0 기준으로 (기본: 절대에너지)")
    args = ap.parse_args()

    paths = [Path(p) for p in args.pdos]
    for p in paths:
        if not p.is_file():
            print(f"[error] '{p}' 파일을 찾을 수 없습니다.")
            sys.exit(1)

    # PDOS 곡선 로드 (한 번만)
    curves = []
    for p in paths:
        E, up, dn = load_two_col(p)
        curves.append((p.stem, E, up, dn))
        print(f"[read] {p}  (label={p.stem})")
    spin = any(dn is not None for _, _, _, dn in curves)

    # 총 DOS 결정
    dos = None
    if not args.no_total:
        dos_path = Path(args.dos) if args.dos else find_total_dos(paths[0].parent)
        if args.dos and not Path(args.dos).is_file():
            print(f"[error] '{args.dos}' 파일을 찾을 수 없습니다.")
            sys.exit(1)
        if dos_path is None:
            print("[info] 같은 폴더에 .DOS(총 DOS)가 없어 PDOS만 그립니다.")
        else:
            dE, dup, ddn = load_two_col(dos_path)
            dtot = dup if ddn is None else dup + ddn
            dos = (dos_path, dE, dtot)
            print(f"[read] {dos_path}  (total DOS)")

    # 페르미 에너지(절대) 결정 + 표시 좌표계 오프셋
    efermi = args.fermi if args.fermi is not None else find_fermi(paths[0].parent)
    off = efermi if (args.fermi_ref and efermi is not None) else 0.0
    if args.fermi_ref and efermi is None:
        print("[info] 페르미 에너지를 못 찾아 -F(E_F 기준) 적용 불가 → 절대에너지로 그립니다.")

    fig, ax = plt.subplots(figsize=(5, 5), dpi=150)

    # 총 DOS: 회색 배경 영역
    if dos is not None:
        _, dE, dtot = dos
        ax.fill_between(dE - off, 0, dtot, color="0.85", zorder=0, label="Total DOS")
        ax.plot(dE - off, dtot, color="0.6", lw=0.8, zorder=1)

    # PDOS 곡선
    colors = ["C0", "C1", "C3", "C2", "C4", "C5", "C6"]
    for idx, (label, E, up, dn) in enumerate(curves):
        c = colors[idx % len(colors)]
        if dn is None:
            ax.plot(E - off, up, color=c, lw=1.3, label=label, zorder=3)
        else:
            ax.plot(E - off,  up, color=c, lw=1.3, label=f"{label} ↑", zorder=3)
            ax.plot(E - off, -dn, color=c, lw=1.3, ls="--", label=f"{label} ↓", zorder=3)

    if spin:
        ax.axhline(0, color="k", lw=0.6)

    # Fermi 세로선: -F 면 0, 아니면 절대 Fermi
    fline = 0.0 if args.fermi_ref else efermi
    if fline is not None:
        ax.axvline(fline, color="gray", lw=0.8, ls="--", label="$E_F$")
    else:
        print("[info] *.EIG 에서 페르미 에너지를 못 찾아 E_F 선을 생략합니다 "
              "(--fermi 로 지정 가능).")
    ax.set_xlabel("$E - E_F$ (eV)" if args.fermi_ref else "$E$ (eV)")
    ax.set_ylabel("DOS (states/eV)")
    ax.set_title(curves[0][0] + " PDOS" if len(curves) == 1 else "PDOS")
    # x 범위(에너지, 표시 좌표계): -e/-E 또는 PDOS 곡선들의 공통 데이터 범위
    xlo = args.emin if args.emin is not None else max(E[0]  - off for _, E, _, _ in curves)
    xhi = args.emax if args.emax is not None else min(E[-1] - off for _, E, _, _ in curves)
    ax.set_xlim(xlo, xhi)
    if not spin:
        ax.set_ylim(bottom=0)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.2)
    fig.tight_layout()

    if len(paths) == 1:
        out = paths[0].parent / f"{paths[0].stem.lower()}_pdos.png"
    else:
        out = paths[0].parent / "pdos_compare.png"
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[saved] {out}")


if __name__ == "__main__":
    main()
