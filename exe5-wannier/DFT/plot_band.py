import numpy as np
import matplotlib.pyplot as plt

nks = 41
nbnd = 24

E_band = np.loadtxt("Fe.bands.dat.gnu").reshape(nbnd,nks,2)

plt.figure()

for i in range(nbnd):
    plt.plot(E_band[i,:,0], E_band[i,:,1], "b-")

plt.xlim([0.0000,3.0731])
plt.xticks([0.0000,1.0000,1.8660,2.3660,3.0731], labels=[r"$\Gamma$", r"H", r"P", r"N", r"$\Gamma$"], fontsize=20)

plt.ylabel("Energy (eV)", fontsize=25)

plt.axvline(1.0000, 0.0, 1.0, color="black", linestyle="dashed", linewidth=1)
plt.axvline(1.8660, 0.0, 1.0, color="black", linestyle="dashed", linewidth=1)
plt.axvline(2.3660, 0.0, 1.0, color="black", linestyle="dashed", linewidth=1)
plt.axhline(17.5502, 0.0, 1.0, color="black", linestyle="dashed", linewidth=1)

plt.savefig("Fe_band.svg", bbox_inches="tight")

plt.figure()

for i in range(nbnd):
    plt.plot(E_band[i,:,0], E_band[i,:,1], "b-")

plt.xlim([0.0000,3.0731])
plt.xticks([0.0000,1.0000,1.8660,2.3660,3.0731], labels=[r"$\Gamma$", r"H", r"P", r"N", r"$\Gamma$"], fontsize=20)

plt.ylim([0,50])
plt.yticks([0,10,20,30,40,50], labels=[0,10,20,30,40,50], fontsize=20)

plt.ylabel("Energy (eV)", fontsize=25)

plt.axvline(1.0000, 0.0, 1.0, color="black", linestyle="dashed", linewidth=1)
plt.axvline(1.8660, 0.0, 1.0, color="black", linestyle="dashed", linewidth=1)
plt.axvline(2.3660, 0.0, 1.0, color="black", linestyle="dashed", linewidth=1)
plt.axhline(17.5502, 0.0, 1.0, color="black", linestyle="dashed", linewidth=1)

plt.savefig("Fe_band_fermi.svg", bbox_inches="tight")