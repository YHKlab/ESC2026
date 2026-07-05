#!/usr/bin/env python3
"""
마스터(v7.5, ortho-atomic) vs 노드(v6.5) 의 Hubbard U band 정량 비교.

각 U값에서 VBM/CBM/gap을 Fermi 기준으로 추출해, U에 따른 이동을 표로 비교.
"눈으로 비슷해 보인다"를 숫자로 확정하기 위한 도구.

전제: bands.x가 만든 .gnu 파일(1열 k, 2열 E[eV]) + scf.out(Fermi)이 있어야 함.

사용:
  # 같은 폴더에 마스터/노드 결과가 접미사로 구분돼 있으면:
  python compare_master_node.py \
      --master-dir ./master --node-dir ./node --scf-master ../5_scf_U_master --scf-node ../5_scf_U

  # 가장 단순: 현재 폴더의 gnu + ../5_scf_U 의 scf.out 만 분석(단일 세트)
  python compare_master_node.py --single
"""
import numpy as np, re, os, glob, argparse

U_VALUES = ["0.0", "1.5", "3.0", "4.5"]
# U값 → scf.out outdir 매핑 (run_scf 스크립트 규칙)
SCF_TAG = {u: f"scf_U{u}.out" for u in U_VALUES}
GNU_TAG = {u: f"MoS2_bands_U{u}.dat.gnu" for u in U_VALUES}

def read_fermi(scf_path):
    """scf.out에서 Fermi energy(eV). 없으면 highest occupied."""
    if not scf_path or not os.path.exists(scf_path):
        return None
    ef = None
    for line in open(scf_path):
        if "the Fermi energy is" in line:
            m = re.search(r"(-?\d+\.\d+)", line);  ef = float(m.group(1)) if m else ef
        elif "highest occupied" in line:
            nums = re.findall(r"(-?\d+\.\d+)", line)
            if nums: ef = float(nums[-1])
    return ef

def load_bands(gnu_path):
    """QE .gnu → (k array, E array). band는 k가 되감기는 지점으로 구분."""
    if not os.path.exists(gnu_path):
        return None
    data = np.loadtxt(gnu_path)
    return data  # (N,2): [:,0]=k, [:,1]=E

def vbm_cbm(gnu_path, ef):
    """
    Fermi 기준으로 VBM(E_F 아래 최댓값), CBM(E_F 위 최솟값), gap 추출.
    metal이면 gap<=0 로 나옴.
    """
    d = load_bands(gnu_path)
    if d is None or ef is None:
        return None
    E = d[:,1] - ef
    occ = E[E < 0]     # 점유 (valence)
    unocc = E[E > 0]   # 비점유 (conduction)
    vbm = occ.max() if occ.size else np.nan
    cbm = unocc.min() if unocc.size else np.nan
    gap = cbm - vbm if (occ.size and unocc.size) else np.nan
    return vbm, cbm, gap

def analyze(label, gnu_dir, scf_dir):
    """한 세트(마스터 또는 노드)의 U별 VBM/CBM/gap 표."""
    rows = []
    for u in U_VALUES:
        gnu = os.path.join(gnu_dir, GNU_TAG[u])
        scf = os.path.join(scf_dir, SCF_TAG[u])
        ef = read_fermi(scf)
        res = vbm_cbm(gnu, ef)
        if res is None:
            rows.append((u, ef, np.nan, np.nan, np.nan)); continue
        vbm, cbm, gap = res
        rows.append((u, ef, vbm, cbm, gap))
    return rows

def print_table(label, rows):
    print(f"\n=== {label} ===")
    print(f"{'U(eV)':>6} {'E_F(eV)':>9} {'VBM':>8} {'CBM':>8} {'gap':>8}  {'ΔVBM':>8} {'ΔCBM':>8}")
    vbm0 = rows[0][2]; cbm0 = rows[0][3]
    for u, ef, vbm, cbm, gap in rows:
        dv = vbm - vbm0 if not np.isnan(vbm) else np.nan
        dc = cbm - cbm0 if not np.isnan(cbm) else np.nan
        ef_s = f"{ef:.3f}" if ef is not None else "  N/A"
        print(f"{u:>6} {ef_s:>9} {vbm:8.3f} {cbm:8.3f} {gap:8.3f}  {dv:8.3f} {dc:8.3f}")
    print("  ΔVBM/ΔCBM = U=0 대비 이동량. 이게 마스터/노드에서 비슷하면 물리 재현 OK.")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--master-dir", default="./master", help="마스터 gnu 폴더")
    ap.add_argument("--node-dir", default="./node", help="노드 gnu 폴더")
    ap.add_argument("--scf-master", default="../5_scf_U_master")
    ap.add_argument("--scf-node", default="../5_scf_U")
    ap.add_argument("--single", action="store_true",
                    help="현재 폴더 gnu + ../5_scf_U 만 단일 분석")
    a = ap.parse_args()

    if a.single:
        rows = analyze("현재 세트", ".", "../5_scf_U")
        print_table("현재 폴더 결과", rows)
        return

    m_rows = analyze("master", a.master_dir, a.scf_master)
    n_rows = analyze("node", a.node_dir, a.scf_node)
    print_table("MASTER (v7.5, ortho-atomic)", m_rows)
    print_table("NODE (v6.5)", n_rows)

    # 핵심: 두 버전의 ΔVBM/ΔCBM 차이 (U 반응이 얼마나 다른가)
    print("\n=== 마스터 vs 노드: U 반응 차이 (핵심 지표) ===")
    print(f"{'U(eV)':>6} {'ΔVBM차':>10} {'ΔCBM차':>10} {'gap차':>10}")
    for i, u in enumerate(U_VALUES):
        try:
            dv_m = m_rows[i][2]-m_rows[0][2]; dv_n = n_rows[i][2]-n_rows[0][2]
            dc_m = m_rows[i][3]-m_rows[0][3]; dc_n = n_rows[i][3]-n_rows[0][3]
            g_m = m_rows[i][4]; g_n = n_rows[i][4]
            print(f"{u:>6} {dv_m-dv_n:10.3f} {dc_m-dc_n:10.3f} {g_m-g_n:10.3f}")
        except Exception:
            print(f"{u:>6}   (데이터 부족)")
    print("\n해석: ΔCBM차가 크면 = conduction band의 U 반응이 두 버전에서 다름(지금 의심 지점).")
    print("      ΔVBM차가 작으면 = valence 물리는 재현됨.")

if __name__ == "__main__":
    main()
