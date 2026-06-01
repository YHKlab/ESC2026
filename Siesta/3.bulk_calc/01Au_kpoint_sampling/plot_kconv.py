import os
import re
import glob
import matplotlib.pyplot as plt

ks = []
energies = []

dirs = [d for d in glob.glob("k*") if os.path.isdir(d)]

for d in sorted(dirs, key=lambda x: int(re.sub(r"\D", "", x))):

    k = int(re.sub(r"\D", "", d))

    fout = os.path.join(d, "RUN.out")

    if not os.path.isfile(fout):
        continue

    energy = None

    with open(fout, "r", errors="ignore") as f:
        for line in f:
            if "siesta:         Total =" in line:
                energy = float(line.split()[-1])

    if energy is not None:
        ks.append(k)
        energies.append(energy)

plt.plot(ks, energies, 'o-')

plt.xlabel("k-point grid")
plt.ylabel("Total Energy (eV)")
plt.title("Au bulk k-point convergence")


plt.ticklabel_format(axis='y', style='plain', useOffset=False)

plt.grid(True)
plt.tight_layout()

plt.savefig("kconv11.png", dpi=300)
print("saved kconv.png")
