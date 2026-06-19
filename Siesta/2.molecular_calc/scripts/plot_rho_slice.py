#!/usr/bin/env python3
"""
전하 밀도 2D 단면 시각화

사용법:
    python scripts/plot_rho_slice.py H2O
    python scripts/plot_rho_slice.py NH3

분자 평면 단면의 rho / delta-rho 를 figures/{label}_rho_slice.png 로 저장.
"""
import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from scipy.ndimage import map_coordinates

SCRIPTS = Path(__file__).resolve().parent
BASE    = SCRIPTS.parent
FIGURES = BASE / "figures"
FIGURES.mkdir(exist_ok=True)

# 중심 원소 및 인접 원소 (슬라이스 평면 정의용)
MOLECULE_CENTER = {"H2O": "O", "NH3": "N", "CH4": "C"}


def load_grid(path: Path):
    import sisl
    return sisl.get_sile(str(path)).read_grid()


def make_slice(grid, center_xyz, v1_xyz, v2_xyz,
               extent: float = 3.0, npix: int = 240):
    """center 기준 v1·v2 평면에서 extent Å 크기의 2D 슬라이스."""
    e_x = v1_xyz / np.linalg.norm(v1_xyz)
    perp = v2_xyz - np.dot(v2_xyz, e_x) * e_x
    e_y  = perp / np.linalg.norm(perp)

    s = np.linspace(-extent, extent, npix)
    U, V = np.meshgrid(s, s, indexing="xy")
    world = (center_xyz[None, None, :]
             + U[..., None] * e_x + V[..., None] * e_y)

    inv_cell = np.linalg.inv(np.asarray(grid.cell))
    frac = world @ inv_cell
    shape = np.array(grid.grid.shape)
    idx = frac * shape
    coords = np.stack([idx[..., i] for i in range(3)], axis=0)
    data = map_coordinates(grid.grid, coords, order=1, mode="grid-wrap")
    return s, data, (e_x, e_y, center_xyz)


def plot_slice(data, s, atoms_info, basis, title, out_path, symmetric=False):
    e_x, e_y, origin = basis
    fig, ax = plt.subplots(figsize=(5, 4.8), dpi=150)
    ext = [s[0], s[-1], s[0], s[-1]]
    if symmetric:
        vmax = float(np.max(np.abs(data))) or 1e-3
        im = ax.imshow(data, origin="lower", extent=ext,
                       cmap="RdBu_r", vmin=-vmax, vmax=vmax)
    else:
        eps = 1e-5
        im = ax.imshow(np.clip(data, eps, None), origin="lower", extent=ext,
                       cmap="viridis", norm=LogNorm(vmin=eps, vmax=data.max()))
    plt.colorbar(im, ax=ax)

    for sym, xyz in atoms_info:
        d = xyz - origin
        px, py = np.dot(d, e_x), np.dot(d, e_y)
        color = {"O": "red", "H": "white", "N": "blue", "C": "black"}.get(sym, "gray")
        ax.scatter(px, py, s=160, c=color, edgecolors="k", lw=1.2, zorder=10)
        ax.annotate(sym, (px, py), ha="center", va="center",
                    fontsize=9, zorder=11)

    ax.set_xlabel("Å"); ax.set_ylabel("Å")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[saved] {out_path}")


def main():
    import sisl

    label = sys.argv[1] if len(sys.argv) > 1 else "H2O"
    mol_dir = BASE / label

    xv_path  = mol_dir / f"{label}.XV"
    rho_path = mol_dir / f"{label}.RHO"
    drho_candidates = [mol_dir / f"{label}.DRHO", mol_dir / f"{label}.DRho"]
    drho_path = next((p for p in drho_candidates if p.exists()), None)

    if not xv_path.exists():
        print(f"[error] {xv_path} not found")
        sys.exit(1)

    geom = sisl.get_sile(str(xv_path)).read_geometry()
    syms = [a.symbol for a in geom.atoms]
    xyz  = geom.xyz

    center_sym = MOLECULE_CENTER.get(label, syms[0])
    c_idx = syms.index(center_sym)
    nbr_idx = [i for i in range(len(syms)) if i != c_idx]

    center  = xyz[c_idx]
    v1 = xyz[nbr_idx[0]] - center
    v2 = xyz[nbr_idx[1]] - center

    atoms_info = list(zip(syms, xyz))

    for path, out_name, symmetric in [
        (rho_path,  f"{label.lower()}_rho_slice.png",  False),
        (drho_path, f"{label.lower()}_drho_slice.png", True),
    ]:
        if path is None or not path.exists():
            print(f"[skip] {path} not found")
            continue
        grid = load_grid(path)
        s, data, basis = make_slice(grid, center, v1, v2)
        kind = "Δρ" if symmetric else "ρ"
        plot_slice(data, s, atoms_info, basis,
                   f"{label} — {kind} (분자 평면 단면)",
                   FIGURES / out_name, symmetric=symmetric)


if __name__ == "__main__":
    main()
