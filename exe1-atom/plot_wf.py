import os
import sys
import matplotlib.pyplot as plt

def parse_atom_file(filename):
    """Parses ATOM text files safely, skipping non-numeric headers."""
    x, y = [], []
    with open(filename, 'r') as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 2:
                try:
                    x.append(float(parts[0]))
                    y.append(float(parts[1]))
                except ValueError:
                    continue
    return x, y

def plot_pair(ae_file, ps_file, title, xlabel, ylabel, xlim_max=None):
    if not os.path.exists(ae_file) or not os.path.exists(ps_file):
        return False

    x_ae, y_ae = parse_atom_file(ae_file)
    x_ps, y_ps = parse_atom_file(ps_file)

    plt.figure(figsize=(8, 5))
    plt.plot(x_ae, y_ae, label='All-Electron (Real)', color='black', linewidth=2)
    plt.plot(x_ps, y_ps, label='Pseudopotential', color='red', linestyle='--', linewidth=2)

    plt.title(title, fontsize=13, fontweight='bold')
    plt.xlabel(xlabel, fontsize=11)
    plt.ylabel(ylabel, fontsize=11)
    
    if xlim_max:
        plt.xlim(0, xlim_max)
        
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(fontsize=10)
    
    output_png = f"plot_{ae_file}_vs_{ps_file}.png"
    plt.savefig(output_png, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Saved: {output_png}")
    return True

def auto_plot_all():
    print("🔍 Scanning directory for ATOM output pairs...")
    
    # 1. Plot Charge Density
    plot_pair('CHARGE', 'PSCHARGE', 'Total Radial Charge Density', 'Radius (bohr)', '4 * pi * r^2 * rho(r)', xlim_max=5.0)

    # Orbital mappings for angular momentum l = 0, 1, 2, 3
    orbitals = {0: 's-orbital', 1: 'p-orbital', 2: 'd-orbital', 3: 'f-orbital'}

    # 2. Loop through Wavefunctions (WFNR)
    for l, orb_name in orbitals.items():
        ae_wf = f'AEWFNR{l}'
        ps_wf = f'PSWFNR{l}'
        if os.path.exists(ae_wf):
            plot_pair(ae_wf, ps_wf, f'Valence Wavefunction ({orb_name})', 'Radius (bohr)', 'r * R(r)', xlim_max=4.0)

    # 3. Loop through Logarithmic Derivatives (LOGD)
    # Note: X-axis for LOGD is Energy (Rydberg), so we omit the radius xlim constraint.
    for l, orb_name in orbitals.items():
        ae_logd = f'AELOGD{l}'
        ps_logd = f'PSLOGD{l}'
        if os.path.exists(ae_logd):
            plot_pair(ae_logd, ps_logd, f'Logarithmic Derivative ({orb_name})', 'Energy (Ry)', 'd/dr ln(Psi)', xlim_max=None)

if __name__ == "__main__":
    # If explicit arguments are given, run single mode (your original behavior)
    if len(sys.argv) >= 3:
        ae_file = sys.argv[1]
        ps_file = sys.argv[2]
        plot_title = sys.argv[3] if len(sys.argv) > 3 else f"{ae_file} vs {ps_file}"
        
        # Check if it's a log derivative to change labels dynamically
        if "LOGD" in ae_file:
            plot_pair(ae_file, ps_file, plot_title, 'Energy (Ry)', 'd/dr ln(Psi)')
        else:
            plot_pair(ae_file, ps_file, plot_title, 'Radius (bohr)', 'Value', xlim_max=5.0)
    else:
        # Batch mode execution
        auto_plot_all()
        print("🎉 All available visual comparisons have been plotted successfully!")