#!/usr/bin/env python3
"""
DOS 그리기 (방법 2: .EIG + .KP 에서 직접 DOS 계산까지 수행)

Eig2DOS 가 하는 일(고유값을 k가중치로 가중합 + 브로드닝)을 파이썬에서 직접 처리.
별도 후처리 도구 없이 .EIG 하나로 총 DOS 를 만들고 그린다.

사용법:
    python /path/to/scripts/plot_dos2.py Graphene.EIG
    python /path/to/scripts/plot_dos2.py Graphene.EIG -s 0.1 -n 2000 -e -25 -E 10

기본적으로 같은 위치의 {label}.KP 를 k가중치로 사용( -k 로 지정 가능).
그림은 .EIG 와 같은 디렉토리에 {label}_dos2.png 로 저장.

DOS 정의 (비자성 nspin=1):
    DOS(E) = 2 * Σ_k w_k Σ_n  g(E - ε_nk)        (Σ_k w_k = 1, ×2 = 스핀 축퇴)
스핀 분극(nspin=2)이면 up/down 채널을 따로 합산.
브로드닝 g 는 가우시안(기본) 또는 로런치안(-l).
"""
import sys
import argparse
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def read_eig(path: Path):
    """SIESTA .EIG 파싱 -> (efermi, eig[nk, nspin, nbands])."""
    toks = path.read_text().split()
    efermi = float(toks[0])
    nbands, nspin, nk = int(toks[1]), int(toks[2]), int(toks[3])

    rest = toks[4:]
    per_k = 1 + nspin * nbands           # 각 k 블록: k-index + nspin*nbands 고유값
    need  = nk * per_k
    arr = np.array(rest[:need], dtype=float).reshape(nk, per_k)
    eig = arr[:, 1:].reshape(nk, nspin, nbands)   # k-index(0열) 제거
    return efermi, eig, nspin


def read_kp_weights(path: Path, nk: int):
    """SIESTA .KP 파싱 -> 정규화된 k가중치 (합 1)."""
    lines = path.read_text().split("\n")
    n = int(lines[0].split()[0])
    w = np.array([float(lines[1 + i].split()[4]) for i in range(n)])
    if n != nk:
        print(f"[warn] .KP의 k점 수({n})와 .EIG({nk})가 다릅니다.")
    s = w.sum()
    return w / s if s > 0 else w


def broaden(E, eps, weights, sigma, lorentz=False):
    """DOS(E) = Σ_i weights_i * g(E - eps_i).  (per spin, 가중치 합=1 기준)"""
    E   = E[:, None]                      # (nE, 1)
    eps = eps[None, :]                    # (1, N)
    x = (E - eps) / sigma
    # Eig2DOS 컨벤션과 일치: smearing σ 는 표준편차가 아니라
    # 가우시안 exp(-(Δ/σ)²)/(σ√π) 의 폭, 로런치안은 HWHM=σ.
    if lorentz:
        g = (1.0 / (np.pi * sigma)) / (1.0 + x ** 2)
    else:
        g = np.exp(-(x ** 2)) / (sigma * np.sqrt(np.pi))
    return (weights[None, :] * g).sum(axis=1)


def main():
    ap = argparse.ArgumentParser(description="Compute & plot total DOS from a SIESTA .EIG file")
    ap.add_argument("eig", help="SIESTA .EIG 파일")
    ap.add_argument("-k", "--kp", help=".KP 파일 (기본: .EIG 를 .KP 로 치환)")
    ap.add_argument("-s", "--smear", type=float, default=0.2, help="브로드닝(eV) [0.2]")
    ap.add_argument("-n", "--npts", type=int, default=1000, help="에너지 점 개수 [1000]")
    ap.add_argument("-e", "--emin", type=float, default=None,
                    help="에너지 최소(eV, 표시 좌표계); 없으면 데이터(고유값) 범위")
    ap.add_argument("-E", "--emax", type=float, default=None,
                    help="에너지 최대(eV, 표시 좌표계); 없으면 데이터(고유값) 범위")
    ap.add_argument("-l", "--lorentz", action="store_true", help="로런치안 브로드닝")
    ap.add_argument("-F", "-f", "--fermi-ref", dest="fermi_ref", action="store_true",
                    help="에너지를 E_F=0 기준으로 (기본: 절대에너지)")
    args = ap.parse_args()

    eig_path = Path(args.eig)
    if not eig_path.is_file():
        print(f"[error] '{eig_path}' 파일을 찾을 수 없습니다.")
        sys.exit(1)
    kp_path = Path(args.kp) if args.kp else eig_path.with_suffix(".KP")
    if not kp_path.is_file():
        print(f"[error] k가중치 파일 '{kp_path}' 가 없습니다. -k 로 지정하세요.")
        sys.exit(1)

    print(f"[read] {eig_path}  /  {kp_path}")
    efermi, eig, nspin = read_eig(eig_path)      # eig: (nk, nspin, nbands)
    nk = eig.shape[0]
    w  = read_kp_weights(kp_path, nk)

    off = efermi if args.fermi_ref else 0.0   # -F 면 E_F 기준, 아니면 절대
    # 표시 좌표계 기준 에너지 범위: -e/-E 또는 데이터(고유값) 범위
    emin = args.emin if args.emin is not None else float((eig - off).min())
    emax = args.emax if args.emax is not None else float((eig - off).max())
    # 표시 격자(xs) -> 계산은 절대 에너지 격자(E)에서
    xs = np.linspace(emin, emax, args.npts)
    E  = xs + off

    # band 축으로 펼치고 k가중치를 band 수만큼 반복
    nbands = eig.shape[2]
    w_rep  = np.repeat(w, nbands)                 # (nk*nbands,)

    dos_spin = []
    for s in range(nspin):
        eps_s = eig[:, s, :].reshape(-1)          # (nk*nbands,)
        dos_spin.append(broaden(E, eps_s, w_rep, args.smear, args.lorentz))

    if nspin == 1:
        n_up = n_dn = dos_spin[0]
        ntot = 2.0 * dos_spin[0]                  # 스핀 축퇴 ×2
    else:
        n_up, n_dn = dos_spin[0], dos_spin[1]
        ntot = n_up + n_dn

    label = eig_path.stem
    x = xs   # 표시 좌표계 (절대 또는 E-E_F)
    print(f"[info] E_F = {efermi:.4f} eV, nspin={nspin}, nk={nk}, "
          f"nbands={nbands}, smear={args.smear} eV "
          f"({'Lorentz' if args.lorentz else 'Gauss'})")

    fig, ax = plt.subplots(figsize=(5, 5), dpi=150)
    ax.plot(x, ntot, color="C0", lw=1.5, label="Total DOS")
    if nspin == 2:
        ax.plot(x,  n_up, color="C3", lw=1.0, ls="--", label="up")
        ax.plot(x, -n_dn, color="C2", lw=1.0, ls="--", label="down")
        ax.axhline(0, color="k", lw=0.6)

    ax.axvline(0 if args.fermi_ref else efermi,
               color="gray", lw=0.8, ls="--", label="$E_F$")
    ax.set_xlabel("$E - E_F$ (eV)" if args.fermi_ref else "$E$ (eV)")
    ax.set_ylabel("DOS (states/eV)")
    ax.set_title(f"{label} DOS (from .EIG)")
    ax.set_xlim(x[0], x[-1])
    if nspin == 1:
        ax.set_ylim(bottom=0)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.2)
    fig.tight_layout()

    out = eig_path.parent / f"{label.lower()}_dos2.png"
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[saved] {out}")


if __name__ == "__main__":
    main()
