#!/usr/bin/env python3
"""
DFT+U 또는 DFT+U+V band 구조 plot.
네가 준 gnuplot 스크립트를 python으로 옮기고, Fermi energy를 각 계산의
scf.out에서 자동 추출하도록 개선 (하드코딩 E_f 제거).

사용:
  python plot_bands_UV.py --gnu MoS2_bands_U3.0.dat.gnu --scfout ../5_scf_U/scf_U3.0.out
  # 여러 U 겹쳐 그리기:
  python plot_bands_UV.py --compare
"""
import numpy as np, matplotlib.pyplot as plt, re, argparse, os, glob

def read_fermi(scfout):
    """scf.out에서 Fermi energy(eV) 추출. 없으면 highest occupied 사용."""
    ef = None
    if not scfout or not os.path.exists(scfout):
        return 0.0
    for line in open(scfout):
        if "the Fermi energy is" in line:
            m = re.search(r"(-?\d+\.\d+)", line)
            if m: ef = float(m.group(1))
        elif "highest occupied" in line:
            nums = re.findall(r"(-?\d+\.\d+)", line)
            if nums: ef = float(nums[-1])
    return ef if ef is not None else 0.0

def load_gnu(gnu):
    """QE bands.x .gnu 파일 → k(1열), E(2열). band별로 빈 줄 구분."""
    if not os.path.exists(gnu): return None, None
    data = np.loadtxt(gnu)
    return data[:,0], data[:,1]

def plot_single(gnu, scfout, out="band.png", emin=-6, emax=6):
    k, e = load_gnu(gnu)
    if k is None:
        print(f"파일 없음: {gnu}"); return
    ef = read_fermi(scfout)
    e = e - ef
    breaks = np.where(np.diff(k) < 0)[0] + 1
    segs = np.split(np.column_stack([k,e]), breaks)
    plt.figure(figsize=(8,6))
    for s in segs:
        plt.plot(s[:,0], s[:,1], 'k-', lw=1)
    plt.axhline(0, color='r', ls='--', lw=1, label=f'E_F ({ef:.2f} eV)')
    plt.ylim(emin, emax); plt.ylabel("E - E_F (eV)"); plt.xlabel("k-path")
    plt.legend(); plt.grid(ls='--', alpha=0.4); plt.tight_layout()
    plt.savefig(out, dpi=150); print(f"저장: {out} (E_F={ef:.3f} eV)")

def plot_compare(emin=-4, emax=4):
    """U=0/1.5/3.0/4.5 겹쳐 그리기 (각자 Fermi 정렬)."""
    U_VALS = ["0.0","1.5","3.0","4.5"]
    COLORS = {"0.0":"#1f77b4","1.5":"#d62728","3.0":"#2ca02c","4.5":"#9467bd"}
    SCFMAP = {"0.0":"../tmp2","1.5":"../tmp3","3.0":"../tmp4","4.5":"../tmp5"}
    plt.figure(figsize=(9,7))
    for u in U_VALS:
        gnu = f"MoS2_bands_U{u}.dat.gnu"
        scfout = f"../5_scf_U/scf_U{u}.out"
        k,e = load_gnu(gnu)
        if k is None:
            print(f"  건너뜀(파일 없음): {gnu}"); continue
        ef = read_fermi(scfout)
        e = e - ef
        breaks = np.where(np.diff(k) < 0)[0] + 1
        segs = np.split(np.column_stack([k,e]), breaks)
        for i,s in enumerate(segs):
            plt.plot(s[:,0], s[:,1], color=COLORS[u], lw=0.9,
                     label=f"U={u} eV" if i==0 else None)
    plt.axhline(0, color='k', ls='--', lw=1)
    plt.ylim(emin, emax); plt.ylabel("Energy - E_F (eV)"); plt.xlabel("k-path")
    plt.title("MoS2 band structure by Hubbard U")
    plt.legend(title="Hubbard U"); plt.grid(ls='--', alpha=0.4); plt.tight_layout()
    plt.savefig("MoS2_bands_U_compare.png", dpi=150)
    print("저장: MoS2_bands_U_compare.png")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--gnu"); ap.add_argument("--scfout")
    ap.add_argument("--compare", action="store_true")
    ap.add_argument("--emin", type=float, default=-4)
    ap.add_argument("--emax", type=float, default=4)
    a = ap.parse_args()
    if a.compare:
        plot_compare(a.emin, a.emax)
    elif a.gnu:
        plot_single(a.gnu, a.scfout, emin=a.emin, emax=a.emax)
    else:
        print("사용: --compare  또는  --gnu FILE.gnu --scfout SCF.out")
