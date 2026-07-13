import os
import numpy as np  # 수식 계산을 위해 새로 추가됨
import matplotlib.pyplot as plt

def parse_pot_file(filename):
    """PSPOTR# 텍스트 파일을 안전하게 읽어 반지름(r)과 포텐셜(V) 배열을 반환합니다."""
    r, v = [], []
    if not os.path.exists(filename):
        return None, None
        
    with open(filename, 'r') as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 2:
                try:
                    r.append(float(parts[0]))
                    v.append(float(parts[1]))
                except ValueError:
                    continue
    return r, v

def plot_all_potentials():
    plt.figure(figsize=(8, 5))
    
    # 1. 기존 데이터 파일(PSPOTR)들 먼저 그리기
    orbitals = {
        0: ('s-orbital', 'blue'),
        1: ('p-orbital', 'red'),
        2: ('d-orbital', 'green'),
        3: ('f-orbital', 'purple')
    }
    
    has_data = False
    for l, (name, color) in orbitals.items():
        filename = f'PSPOTR{l}'
        r, v = parse_pot_file(filename)
        
        if r is not None:
            plt.plot(r, v, label=f'V_{name[0]} (l={l})', color=color, linewidth=2)
            has_data = True
            
    if not has_data:
        print("❌ 에러: 폴더에 PSPOTR0, PSPOTR1 등의 파일이 존재하지 않습니다.")
        return

    # ====================================================================
    # 2.여기에 추가되었습니다! (데이터 플롯 완료 후, 저장 직전 위치)
    # ====================================================================
    # 0.01부터 4.0보어까지 촘촘한 반지름 배열 생성 (0으로 나누기 방지)
    r_dense = np.linspace(0.01, 4.0, 500)

    # (A) 핵 근처의 진짜 All-Electron 전하 포텐셜 (Silicon Z = 14)
    v_ae_total = -14.0 / r_dense
    plt.plot(r_dense, v_ae_total, label='True AE Nucleus (-14/r)', 
             color='black', linestyle=':', alpha=0.4)

    # (B) 핵심부 전자가 가려진 바깥쪽 유효 포텐셜 (Valence Z_val = 4)
    v_ae_screened = -4.0 / r_dense
    plt.plot(r_dense, v_ae_screened, label='Screened Valence Horizon (-4/r)', 
             color='gray', linestyle='--', alpha=0.6)
    # ====================================================================

    # 3. 그래프 스타일 지정 및 저장
    plt.title('Silicon Ionic Pseudopotentials (with AE baseline)', fontsize=14, fontweight='bold')
    plt.xlabel('Radius (bohr)', fontsize=12)
    plt.ylabel('Potential (Ry)', fontsize=12)
    
    plt.xlim(0, 4.0)
    plt.ylim(-15, 2)  # AE 라인이 무한대로 떨어지므로 y축 상한선을 묶어줘야 합니다.
    
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(fontsize=11, loc='lower right')
    
    output_png = "plot_pseudopotential.png"
    plt.savefig(output_png, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"🎉 전전자 가이드라인이 포함된 의포텐셜 그림 저장 완료: {output_png}")

if __name__ == "__main__":
    plot_all_potentials()