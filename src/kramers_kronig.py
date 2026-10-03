"""Kramers-Kronig transform: molar extinction -> molar n' change (beta).

Implements Eq. 1 (Kramers-Kronig) of Ou et al., Science 385, eadm6869 (2024),
combined with Eq. 6 to yield the molar n' change coefficient beta(lambda) in M^-1:

    beta(lambda) = (1 / (2*pi^2)) * P.V. int_0^inf alpha(lambda') * lambda'^2 / (lambda'^2 - lambda^2) dlambda'

where alpha is the molar extinction coefficient (M^-1 cm^-1) and lambda is in cm.
The Cauchy principal value is handled by excluding the singular point lambda' = lambda
from the discrete sum (standard for tabulated data).

CLI: python src/kramers_kronig.py --input <csv> --outdir <dir>
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

NM_TO_CM = 1e-7


def load_spectrum(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Read lambda_nm and alpha_input_M-1 columns from a ';'-separated CSV."""
    data = np.loadtxt(path, delimiter=";", skiprows=1, usecols=(0, 1))
    if data.ndim != 2 or data.shape[1] < 2:
        raise ValueError(f"CSV must have at least 2 numeric columns: {path}")
    lam_nm = data[:, 0]
    alpha = data[:, 1]
    if np.any(np.diff(lam_nm) <= 0):
        raise ValueError("Wavelengths must be strictly increasing")
    return lam_nm, alpha


def kramers_kronig_beta(lam_nm: np.ndarray, alpha: np.ndarray) -> np.ndarray:
    """Molar n' change beta(lambda) in M^-1 from molar extinction alpha (M^-1 cm^-1).

    Cauchy principal value via discrete sum excluding the singular point.
    """
    lam_cm = lam_nm * NM_TO_CM
    n = len(lam_cm)
    beta = np.empty(n)
    for i in range(n):
        li = lam_cm[i]
        mask = np.arange(n) != i
        lj = lam_cm[mask]
        aj = alpha[mask]
        # integrand alpha(l') * l'^2 / (l'^2 - l^2); trapezoid over uniform grid
        integrand = aj * lj**2 / (lj**2 - li**2)
        beta[i] = np.trapezoid(integrand, lj)
    return beta / (2.0 * np.pi**2)


def plot_input(lam_nm: np.ndarray, alpha: np.ndarray, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(lam_nm, alpha, lw=1.5)
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel(r"Molar extinction $\alpha$ (M$^{-1}$ cm$^{-1}$)")
    ax.set_title("Input spectrum: tartrazine molar extinction")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def plot_result(lam_nm: np.ndarray, beta: np.ndarray, ref: tuple[float, float] | None, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(lam_nm, beta, lw=1.5, label="KK result")
    if ref is not None:
        ax.plot(ref[0], ref[1], "ro", label=f"ref {ref[0]} nm = {ref[1]} M$^{{-1}}$")
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel(r"Molar n' change $\beta$ (M$^{-1}$)")
    ax.set_title("Kramers-Kronig: molar n' change of tartrazine")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Kramers-Kronig molar n' change")
    parser.add_argument("--input", type=Path, default=Path("data/other/tartrazine_kk_results.csv"))
    parser.add_argument("--outdir", type=Path, default=Path("memory"))
    args = parser.parse_args()

    lam_nm, alpha = load_spectrum(args.input)
    beta = kramers_kronig_beta(lam_nm, alpha)

    args.outdir.mkdir(parents=True, exist_ok=True)
    plot_input(lam_nm, alpha, args.outdir / "1.1_03-10-2026_input-spectrum.png")
    plot_result(lam_nm, beta, (500.0, 0.198), args.outdir / "1.2_03-10-2026_kk-result.png")

    out_csv = args.outdir / "1.3_03-10-2026_kk-result.csv"
    np.savetxt(out_csv, np.column_stack([lam_nm, beta]), delimiter=";",
               header="lambda_nm;beta_M-1", comments="")

    # quick self-check against Table 1 reference
    idx = int(np.argmin(np.abs(lam_nm - 500.0)))
    print(f"beta(500 nm) = {beta[idx]:.4f} M^-1  (ref 0.198)")
    print(f"wrote: {args.outdir}")


if __name__ == "__main__":
    main()