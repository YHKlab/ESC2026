import os
import glob
import numpy as np
import matplotlib.pyplot as plt

lv = np.array([
    [0.81649, 0.28867, 0.50000],
    [0.00000, 0.86602, 0.50000],
    [0.00000, 0.00000, 1.00000],
])

det_lv = abs(np.linalg.det(lv))

alist = []
energies = []

for d in glob.glob("a*"):
    if not os.path.isdir(d):
        continue

    try:
        a = float(d[1:])
    except ValueError:
        continue

    fout = os.path.join(d, "RUN.out")
    if not os.path.isfile(fout):
        continue

    E = None
    with open(fout, "r", errors="ignore") as f:
        for line in f:
            if "siesta:         Total =" in line:
                E = float(line.split()[-1])

    if E is not None:
        alist.append(a)
        energies.append(E)

alist = np.array(alist)
energies = np.array(energies)

idx = np.argsort(alist)
alist = alist[idx]
energies = energies[idx]

# FCC conventional volume
V_prim = det_lv * alist**3
V_fcc = 4.0 * V_prim
a_fcc = V_fcc**(1.0 / 3.0)

imin = np.argmin(energies)

print("===== FCC primitive structure =====")
print("LatticeVectors:")
for row in lv:
    print(f"{row[0]:10.5f} {row[1]:10.5f} {row[2]:10.5f}")
print(f"det(LatticeVectors) = {det_lv:.8f}")
print()

print("===== Data =====")
print("# SIESTA_LatticeConstant  FCC_volume(A^3)  FCC_a(A)  TotalEnergy(eV)")
for a, vf, af, e in zip(alist, V_fcc, a_fcc, energies):
    print(f"{a:10.5f} {vf:16.8f} {af:12.6f} {e:18.10f}")

print()
print("===== Minimum data point =====")
print(f"SIESTA LatticeConstant = {alist[imin]:.6f} Ang")
print(f"FCC conventional volume = {V_fcc[imin]:.6f} Ang^3")
print(f"FCC conventional a      = {a_fcc[imin]:.6f} Ang")
print(f"Total energy            = {energies[imin]:.10f} eV")

with open("fcc_volume_energy_raw.dat", "w") as f:
    f.write("# SIESTA_LatticeConstant_A FCC_volume_A3 FCC_a_A TotalEnergy_eV\n")
    for a, vf, af, e in zip(alist, V_fcc, a_fcc, energies):
        f.write(f"{a:12.6f} {vf:18.10f} {af:14.8f} {e:18.10f}\n")

plt.figure()
plt.plot(V_fcc, energies, 'o-', label="SIESTA data")

plt.plot(V_fcc[imin], energies[imin], 's', markersize=8, label="Minimum data point")
plt.annotate(
    f"min\nSIESTA a={alist[imin]:.3f} Å\nFCC a={a_fcc[imin]:.3f} Å",
    xy=(V_fcc[imin], energies[imin]),
    xytext=(V_fcc[imin] + 1.5, energies[imin] + 0.03),
    arrowprops=dict(arrowstyle="->")
)

plt.xlabel("FCC conventional cell volume (Ang^3)")
plt.ylabel("Total Energy (eV)")
plt.title("Au bulk FCC volume-energy curve")
plt.ticklabel_format(axis='y', style='plain', useOffset=False)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("fcc_volume_energy_raw.png", dpi=300)

print()
print("Saved: fcc_volume_energy_raw.dat")
print("Saved: fcc_volume_energy_raw.png")
