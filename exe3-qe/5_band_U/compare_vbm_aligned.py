#!/usr/bin/env python3
"""
마스터 vs 노드 band를 VBM 기준으로 정렬해 비교.
E_F 정렬(기존)이 U에 따라 반대로 움직여 생긴 착시를 제거하기 위함.

가설: gap이 3자리까지 동일하므로, VBM을 0으로 맞추면 두 버전 band가 거의 겹친다.
      = "물리는 같고 E_F 기준선만 버전 간 다르다" 를 시각적으로 증명.

사용:
  python compare_vbm_aligned.py \
    --master-dir ./5_band_U_master --node-dir ./5_band_U_node \
    --scf-master ./5_scf_U --scf-node ./5_scf_U_node
"""
import numpy as np, matplotlib.pyplot as plt, re, os, argparse

U_VALUES = ["0.0","1.5","3.0","4.5"]
COLORS   = {"0.0":"#1f77b4","1.5":"#d62728","3.0":"#2ca02c","4.5":"#9467bd"}

def read_fermi(p):
    if not p or not os.path.exists(p): return None
    ef=None
    for line in open(p):
        if "the Fermi energy is" in line:
            m=re.search(r"(-?\d+\.\d+)",line); ef=float(m.group(1)) if m else ef
        elif "highest occupied" in line:
            n=re.findall(r"(-?\d+\.\d+)",line); ef=float(n[-1]) if n else ef
    return ef

def load(p):
    return np.loadtxt(p) if os.path.exists(p) else None

def get_vbm(d, ef):
    """E_F 기준 valence 최댓값의 '절대 에너지' 반환 (VBM 정렬용)."""
    if d is None or ef is None: return None
    E = d[:,1]
    occ = E[E < ef]
    return occ.max() if occ.size else None

def segments(d):
    k=d[:,0]; brk=np.where(np.diff(k)<0)[0]+1
    return np.split(d, brk)

def plot_set(ax, gnu_dir, scf_dir, title):
    for u in U_VALUES:
        gnu=os.path.join(gnu_dir,f"MoS2_bands_U{u}.dat.gnu")
        scf=os.path.join(scf_dir,f"scf_U{u}.out")
        d=load(gnu); ef=read_fermi(scf)
        vbm=get_vbm(d,ef)
        if d is None or vbm is None:
            print(f"  건너뜀: {gnu}"); continue
        for i,s in enumerate(segments(d)):
            ax.plot(s[:,0], s[:,1]-vbm, color=COLORS[u], lw=0.8,
                    label=f"U={u}" if i==0 else None)
    ax.axhline(0,color="k",ls="--",lw=1)
    ax.set_title(title); ax.set_ylim(-3,4)
    ax.set_xlabel("k-path"); ax.grid(ls="--",alpha=0.3); ax.legend(fontsize=8)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--master-dir",required=True); ap.add_argument("--node-dir",required=True)
    ap.add_argument("--scf-master",required=True); ap.add_argument("--scf-node",required=True)
    a=ap.parse_args()

    fig,axes=plt.subplots(1,2,figsize=(14,6),sharey=True)
    plot_set(axes[0],a.master_dir,a.scf_master,"MASTER (v7.5) — VBM aligned")
    plot_set(axes[1],a.node_dir,a.scf_node,"NODE (v6.5) — VBM aligned")
    axes[0].set_ylabel("E - VBM (eV)")
    fig.suptitle("VBM 기준 정렬: 두 버전이 겹치면 '물리 동일, E_F 기준만 다름' 확정")
    plt.tight_layout(); plt.savefig("compare_vbm_aligned.png",dpi=150)
    print("저장: compare_vbm_aligned.png")

    # 정량: VBM 정렬 후 CBM 위치(=gap)가 U별로 두 버전 동일한지
    print(f"\n{'U':>5} {'master gap':>11} {'node gap':>10} {'차이':>8}")
    for u in U_VALUES:
        row=[]
        for gdir,sdir in [(a.master_dir,a.scf_master),(a.node_dir,a.scf_node)]:
            d=load(os.path.join(gdir,f"MoS2_bands_U{u}.dat.gnu"))
            ef=read_fermi(os.path.join(sdir,f"scf_U{u}.out"))
            vbm=get_vbm(d,ef)
            if d is None or vbm is None: row.append(np.nan); continue
            E=d[:,1]-vbm
            cbm=E[E>0.01].min() if (E>0.01).any() else np.nan  # VBM 위 최솟값
            row.append(cbm)
        diff=row[0]-row[1] if not any(np.isnan(row)) else np.nan
        print(f"{u:>5} {row[0]:11.3f} {row[1]:10.3f} {diff:8.3f}")
    print("→ 차이가 ~0이면 VBM 정렬 시 두 버전 gap 완전 일치 = 물리 동일 확정")

if __name__=="__main__":
    main()
