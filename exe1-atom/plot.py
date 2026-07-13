import os
import sys
import matplotlib.pyplot as plt

def plot_atom_data(ae_filename, ps_filename, title="Atom Data Comparison"):
    # 파일 존재 여부 확인
    if not os.path.exists(ae_filename) or not os.path.exists(ps_filename):
        print(f"❌ 에러: {ae_filename} 또는 {ps_filename} 파일이 현재 폴더에 없습니다.")
        return

    # 데이터 로드 (첫 번째 열: Radius, 두 번째 열: Value)
    r_ae, val_ae = [], []
    r_ps, val_ps = [], []

    with open(ae_filename, 'r') as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 2:
                try:
                    r_ae.append(float(parts[0]))
                    val_ae.append(float(parts[1]))
                except ValueError:
                    continue

    with open(ps_filename, 'r') as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 2:
                try:
                    r_ps.append(float(parts[0]))
                    val_ps.append(float(parts[1]))
                except ValueError:
                    continue

    # 그래프 그리기
    plt.figure(figsize=(8, 5))
    plt.plot(r_ae, val_ae, label='All-Electron (Real)', color='black', linewidth=2)
    plt.plot(r_ps, val_ps, label='Pseudopotential', color='red', linestyle='--', linewidth=2)

    # 그래프 꾸미기
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel('Radius (bohr)', fontsize=12)
    plt.ylabel('Value', fontsize=12)
    plt.xlim(0, 5)  # 보통 핵 근처(0~5 bohr)에서 두 매칭 포인트의 차이가 잘 보입니다.
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(fontsize=11)
    
    # 저장 파일명 결정
    output_png = f"plot_{ae_filename}_{ps_filename}.png"
    plt.savefig(output_png, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"🎉 그래프 시각화 완료! 파일이 저장되었습니다: {output_png}")

if __name__ == "__main__":
    # 터미널 매개변수가 부족할 때 가이드 제공
    if len(sys.argv) < 3:
        print("💡 사용법: python plot_atom.py <AE파일명> <PS파일명> [그래프제목]")
        print("👉 예시: python plot_atom.py AEWFNR0 PSWFNR0 \"Silicon s-orbital Wavefunction\"")
        sys.exit(1)

    ae_file = sys.argv[1]
    ps_file = sys.argv[2]
    plot_title = sys.argv[3] if len(sys.argv) > 3 else f"{ae_file} vs {ps_file}"

    plot_atom_data(ae_file, ps_file, plot_title)