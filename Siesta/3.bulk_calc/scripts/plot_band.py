#!/usr/bin/env python3
"""
밴드 구조 그리기 (SIESTA 후처리 도구 gnubands 출력 .dat 를 읽어 그리기)

밴드 곡선은 gnubands 의 .dat 에서, 고대칭점(Γ/M/K…) tick 은 SIESTA .bands 파일
끝의 tick 블록에서 읽는다.

준비:
    gnubands -F Graphene.bands > Graphene.bands.dat
      -F        : 에너지를 E_F = 0 으로 이동
      -e / -E   : 에너지 범위 지정 (이 스크립트는 .dat 범위 그대로 그림)
사용법:
    python /path/to/scripts/plot_band.py Graphene.bands.dat
    python /path/to/scripts/plot_band.py Graphene.bands.dat --bands Graphene.bands

gnubands .dat 컬럼: k  E[eV]  spin,  밴드마다 빈 줄로 구분된 블록.
헤더의 '# E_F / orig = A  B' 에서 A(현재 좌표계의 Fermi)를 읽어 수평선으로 표시.
tick 은 같은 폴더의 .bands 를 자동으로 찾아 읽는다(없으면 tick 없이 그림).
그림은 .dat 와 같은 디렉토리에 {label}_band.png 로 저장.
"""
import sys
import re
import argparse
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def read_gnubands(path: Path):
    """gnubands .dat -> (ef_cur, ef_orig, [band_block, ...]).  block: (nk,3)=k,E,spin.
    헤더 '# E_F / orig = A  B' : A=현재 좌표계의 Fermi, B=원래(절대) Fermi."""
    ef_cur = ef_orig = None
    blocks, cur = [], []
    for line in path.read_text().splitlines():
        if line.startswith("#"):
            if "E_F" in line and "=" in line:
                try:
                    vals = line.split("=")[1].split()
                    ef_cur = float(vals[0])
                    ef_orig = float(vals[1]) if len(vals) > 1 else ef_cur
                except (ValueError, IndexError):
                    pass
            continue
        if line.strip() == "":
            if cur:
                blocks.append(np.array(cur)); cur = []
            continue
        p = line.split()
        cur.append([float(p[0]), float(p[1]), float(p[2]) if len(p) > 2 else 1.0])
    if cur:
        blocks.append(np.array(cur))
    return ef_cur, ef_orig, blocks


def find_bands(dat_path: Path, override=None):
    """tick 을 읽을 .bands 파일을 찾는다."""
    if override:
        return Path(override)
    cand = dat_path.with_suffix("")          # Graphene.bands.dat -> Graphene.bands
    if cand.suffix == ".bands" and cand.is_file():
        return cand
    bs = sorted(dat_path.parent.glob("*.bands"))
    return bs[0] if bs else None


def read_bands_ticks(path: Path):
    """SIESTA .bands 끝의 tick 블록에서 (위치, 라벨) 추출.
    tick 줄 형식:  <k위치>  'label'  (라벨이 따옴표로 감싸짐)."""
    ticks, labels = [], []
    for line in path.read_text().splitlines():
        m = re.match(r"\s*([-\d.eE]+)\s+'([^']*)'", line)
        if m:
            lab = m.group(2).replace("\\Gamma", "Γ")
            labels.append("Γ" if lab in ("G", "Gamma") else lab)
            ticks.append(float(m.group(1)))
    return ticks, labels


def main():
    ap = argparse.ArgumentParser(description="Plot a SIESTA band structure from gnubands .dat")
    ap.add_argument("dat", help="gnubands 출력 .dat 파일")
    ap.add_argument("--bands", help="tick 을 읽을 .bands 파일 (기본: 같은 폴더 자동 탐색)")
    ap.add_argument("-e", "--emin", type=float, default=None,
                    help="표시할 에너지 최소(eV); 없으면 데이터 범위")
    ap.add_argument("-E", "--emax", type=float, default=None,
                    help="표시할 에너지 최대(eV); 없으면 데이터 범위")
    ap.add_argument("-F", "-f", "--fermi-ref", dest="fermi_ref", action="store_true",
                    help="에너지를 E_F=0 기준으로 (기본: 절대에너지)")
    args = ap.parse_args()

    dat_path = Path(args.dat)
    if not dat_path.is_file():
        print(f"[error] '{dat_path}' 파일을 찾을 수 없습니다.")
        sys.exit(1)

    print(f"[read] {dat_path}")
    ef_cur, ef_orig, blocks = read_gnubands(dat_path)
    if not blocks:
        print("[error] 밴드 데이터를 찾지 못했습니다.")
        sys.exit(1)

    # 데이터 -> 절대에너지 복원: E_abs = E_data + (ef_orig - ef_cur)
    # (gnubands -F 로 이미 이동된 경우 보정). 표시 오프셋: -F 면 절대 Fermi, 아니면 0.
    corr = (ef_orig - ef_cur) if (ef_orig is not None and ef_cur is not None) else 0.0
    efermi_abs = ef_orig
    off = efermi_abs if (args.fermi_ref and efermi_abs is not None) else 0.0

    label = dat_path.stem
    if label.endswith(".bands"):
        label = label[:-6]

    fig, ax = plt.subplots(figsize=(5, 6), dpi=150)
    spin_colors = {1.0: "C0", 2.0: "C3"}
    for blk in blocks:
        s = blk[0, 2] if blk.shape[1] > 2 else 1.0
        k = blk[:, 0].copy()
        E = blk[:, 1].copy() + corr - off          # 표시 좌표계로 변환
        # gnubands 가 범위 밖 점을 빼면서 생긴 k-gap 에서 선을 끊는다.
        if len(k) > 2:
            dk = np.diff(k)
            gaps = np.where(dk > 3.0 * np.median(dk))[0]
            if len(gaps):
                k = np.insert(k, gaps + 1, np.nan)
                E = np.insert(E, gaps + 1, np.nan)
        ax.plot(k, E, color=spin_colors.get(s, "C0"), lw=0.8, alpha=0.8)

    # Fermi 수평선: -F 면 0, 아니면 절대 Fermi
    fline = 0.0 if args.fermi_ref else efermi_abs
    if fline is not None:
        ax.axhline(fline, color="gray", lw=0.8, ls="--", label="$E_F$")
    ax.set_ylabel("$E - E_F$ (eV)" if args.fermi_ref else "$E$ (eV)")

    # 고대칭점 tick: .bands 에서 읽기
    bpath = find_bands(dat_path, args.bands)
    if bpath is not None:
        ticks, tlabels = read_bands_ticks(bpath)
        if ticks:
            print(f"[read] {bpath}  (ticks: {', '.join(tlabels)})")
            for tk in ticks:
                ax.axvline(tk, color="k", lw=0.6)
            ax.set_xticks(ticks)
            ax.set_xticklabels(tlabels)
    else:
        print("[info] .bands 를 찾지 못해 고대칭점 tick 없이 그립니다 (--bands 로 지정 가능).")

    # x 축은 k 데이터 범위, y 축(에너지)은 -e/-E 또는 데이터 범위 (표시 좌표계)
    kmin = min(blk[:, 0].min() for blk in blocks)
    kmax = max(blk[:, 0].max() for blk in blocks)
    emin = args.emin if args.emin is not None else min((blk[:, 1] + corr - off).min() for blk in blocks)
    emax = args.emax if args.emax is not None else max((blk[:, 1] + corr - off).max() for blk in blocks)
    ax.set_xlim(kmin, kmax)
    ax.set_ylim(emin, emax)
    ax.set_title(f"{label} band structure")
    if fline is not None:
        ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()

    out = dat_path.parent / f"{label.lower()}_band.png"
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[saved] {out}")


if __name__ == "__main__":
    main()
