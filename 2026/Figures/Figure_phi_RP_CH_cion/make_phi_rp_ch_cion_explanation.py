from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
SOLVER_DIR = ROOT / "Mixed_Potential_Electrical_Double_Layer"
OUT_DIR = Path(__file__).resolve().parent
CSV_DIR = OUT_DIR / "csv"
INPUTS_DIR = OUT_DIR / "inputs"

sys.path.insert(0, str(SOLVER_DIR))
import Solve_Emix_updating as solver  # noqa: E402


TAG = "homogeneous_E040_PZC060"
E_VALUE = 0.40
PZC_VALUE = 0.60
FIXED_C_ION_M = 1.0e-2
FIXED_C_H = 0.20

C_H_POINTS = np.asarray([0.02, 0.05, 0.10, 0.20, 0.40, 1.00, 2.00], dtype=float)
C_ION_POINTS_M = np.asarray([1.0e-4, 1.0e-3, 1.0e-2, 1.0e-1, 1.0], dtype=float)
C_H_GRID = np.logspace(np.log10(0.02), np.log10(2.0), 180)
C_ION_GRID_M = np.logspace(-4, 0, 180)

COLORS = {
    "ch": "#F26B38",
    "cion": "#12355B",
    "dark": "#272727",
    "gray": "#767676",
    "light": "#E8E8E8",
}


def apply_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Helvetica", "Nimbus Sans", "Arial", "DejaVu Sans", "sans-serif"],
            "font.size": 8.4,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.linewidth": 0.9,
            "legend.frameon": False,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "mathtext.fontset": "custom",
            "mathtext.rm": "Nimbus Sans",
            "mathtext.it": "Nimbus Sans:italic",
            "mathtext.bf": "Nimbus Sans:bold",
            "mathtext.cal": "Nimbus Sans",
            "mathtext.sf": "Nimbus Sans",
            "mathtext.tt": "Nimbus Sans",
        }
    )


def homogeneous_params(c_h: float, c_ion_m: float) -> dict[str, Any]:
    params = solver.default_params()
    params.update(
        {
            "C_tot": solver.concentration_M_to_mol_per_m3(float(c_ion_m)),
            "lambda_D": None,
            "L_Au": 25.0e-9,
            "L_gap": 10.0e-9,
            "L_Pd_len": 25.0e-9,
            "Cdl_Au": float(c_h),
            "Cdl_C": float(c_h),
            "Cdl_Pd": float(c_h),
            "g_Au": None,
            "g_C": None,
            "g_Pd": None,
            "pzc_Au": PZC_VALUE,
            "pzc_C": PZC_VALUE,
            "pzc_Pd": PZC_VALUE,
            "N_modes": 80,
            "Nx": 1200,
            "dh_violation_action": "ignore",
        }
    )
    return params


def phi_rp_formula(c_h: float | np.ndarray, c_ion_m: float | np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    c_h_arr = np.asarray(c_h, dtype=float)
    c_ion_arr = np.asarray(c_ion_m, dtype=float)
    c_h_b, c_ion_b = np.broadcast_arrays(c_h_arr, c_ion_arr)

    lambda_d = np.empty_like(c_ion_b, dtype=float)
    epsilon_s = np.empty_like(c_ion_b, dtype=float)
    for index in np.ndindex(c_ion_b.shape):
        derived = solver.compute_derived_params(homogeneous_params(float(c_h_b[index]), float(c_ion_b[index])))
        lambda_d[index] = float(derived["lambda_D"])
        epsilon_s[index] = float(derived["epsilon_s"])

    g = lambda_d * c_h_b / epsilon_s
    phi_rp = (g / (1.0 + g)) * (E_VALUE - PZC_VALUE)
    return phi_rp, g, lambda_d


def phi_rp_numeric(c_h: float, c_ion_m: float) -> dict[str, float]:
    params = homogeneous_params(c_h, c_ion_m)
    edl = solver.EDLModel(params)
    _x, phi_tilde = edl.phi_tilde_surface(E_VALUE)
    scale = float(params["R"]) * float(params["T"]) / float(params["F"])
    phi_v = np.asarray(phi_tilde, dtype=float) * scale
    analytic, g, lambda_d = phi_rp_formula(c_h, c_ion_m)
    return {
        "C_H_F_per_m2": float(c_h),
        "c_ion_M": float(c_ion_m),
        "g": float(np.asarray(g)),
        "lambda_D_nm": float(np.asarray(lambda_d) * 1.0e9),
        "phi_RP_V": float(np.mean(phi_v)),
        "phi_RP_min_V": float(np.min(phi_v)),
        "phi_RP_max_V": float(np.max(phi_v)),
        "phi_RP_formula_V": float(np.asarray(analytic)),
    }


def write_csv(path: Path, rows: list[dict[str, float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def save_inputs() -> None:
    INPUTS_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "tag": TAG,
        "description": "Homogeneous single-surface EDL check for E < PZC.",
        "E_V_vs_RHE": E_VALUE,
        "PZC_V_vs_RHE": PZC_VALUE,
        "fixed_c_ion_M_for_C_H_sweep": FIXED_C_ION_M,
        "fixed_C_H_F_per_m2_for_c_ion_sweep": FIXED_C_H,
        "C_H_points_F_per_m2": C_H_POINTS.tolist(),
        "c_ion_points_M": C_ION_POINTS_M.tolist(),
        "formula": "phi_RP = [g/(1+g)]*(E-PZC), g=lambda_D*C_H/epsilon_s",
        "solver_source": str(SOLVER_DIR / "Solve_Emix_updating.py"),
    }
    with (INPUTS_DIR / f"inputs_{TAG}.json").open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def build_data() -> tuple[list[dict[str, float]], list[dict[str, float]], list[dict[str, float]]]:
    ch_rows = [phi_rp_numeric(float(c_h), FIXED_C_ION_M) for c_h in C_H_POINTS]
    cion_rows = [phi_rp_numeric(FIXED_C_H, float(c_m)) for c_m in C_ION_POINTS_M]

    heatmap_rows: list[dict[str, float]] = []
    c_h_mesh, c_ion_mesh = np.meshgrid(C_H_GRID, C_ION_GRID_M)
    phi_mesh, g_mesh, lambda_mesh = phi_rp_formula(c_h_mesh, c_ion_mesh)
    for c_h, c_m, phi, g_val, lambda_d in zip(
        c_h_mesh.ravel(),
        c_ion_mesh.ravel(),
        phi_mesh.ravel(),
        g_mesh.ravel(),
        lambda_mesh.ravel(),
    ):
        heatmap_rows.append(
            {
                "C_H_F_per_m2": float(c_h),
                "c_ion_M": float(c_m),
                "g": float(g_val),
                "lambda_D_nm": float(lambda_d * 1.0e9),
                "phi_RP_V": float(phi),
            }
        )
    return ch_rows, cion_rows, heatmap_rows


def style_axis(ax: plt.Axes, xlabel: str, ylabel: str, title: str) -> None:
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc="left", fontsize=9.4, pad=5)
    ax.tick_params(length=3.2, width=0.85, labelsize=8.0)
    ax.spines["left"].set_color(COLORS["dark"])
    ax.spines["bottom"].set_color(COLORS["dark"])


def plot_ch_sweep(ax: plt.Axes, rows: list[dict[str, float]]) -> None:
    phi, _g, _lambda_d = phi_rp_formula(C_H_GRID, FIXED_C_ION_M)
    ax.plot(C_H_GRID, 1000.0 * phi, color=COLORS["ch"], linewidth=2.0)
    ax.scatter(
        [row["C_H_F_per_m2"] for row in rows],
        [1000.0 * row["phi_RP_V"] for row in rows],
        color=COLORS["ch"],
        edgecolor="white",
        linewidth=0.7,
        s=28,
        zorder=4,
    )
    ax.axhline(0.0, color=COLORS["dark"], linewidth=0.75)
    ax.axvline(FIXED_C_H, color=COLORS["gray"], linestyle=(0, (3, 2)), linewidth=0.85)
    ax.set_xscale("log")
    ax.set_xlim(float(C_H_GRID[0]), float(C_H_GRID[-1]))
    ax.set_ylim(-190.0, 8.0)
    ax.annotate(
        r"$C_{\mathrm{H}}$ increases:"
        "\n"
        "more negative",
        xy=(0.74, -150.0),
        xytext=(0.12, -96.0),
        arrowprops=dict(arrowstyle="->", color=COLORS["dark"], linewidth=0.85),
        fontsize=7.2,
        color=COLORS["dark"],
        ha="center",
        va="center",
    )
    style_axis(
        ax,
        r"Helmholtz capacitance, $C_{\mathrm{H}}$ (F/m$^2$)",
        r"$\phi_{\mathrm{RP}}$ (mV)",
        r"At fixed $c_{\mathrm{ion}}=0.01$ M",
    )


def plot_cion_sweep(ax: plt.Axes, rows: list[dict[str, float]]) -> None:
    phi, _g, _lambda_d = phi_rp_formula(FIXED_C_H, C_ION_GRID_M)
    ax.plot(C_ION_GRID_M, 1000.0 * phi, color=COLORS["cion"], linewidth=2.0)
    ax.scatter(
        [row["c_ion_M"] for row in rows],
        [1000.0 * row["phi_RP_V"] for row in rows],
        color=COLORS["cion"],
        edgecolor="white",
        linewidth=0.7,
        s=28,
        zorder=4,
    )
    ax.axhline(0.0, color=COLORS["dark"], linewidth=0.75)
    ax.axvline(FIXED_C_ION_M, color=COLORS["gray"], linestyle=(0, (3, 2)), linewidth=0.85)
    ax.set_xscale("log")
    ax.set_xlim(float(C_ION_GRID_M[0]), float(C_ION_GRID_M[-1]))
    ax.set_ylim(-190.0, 8.0)
    ax.annotate(
        r"$c_{\mathrm{ion}}$ increases:"
        "\n"
        "shifts toward 0",
        xy=(0.35, -24.0),
        xytext=(0.006, -58.0),
        arrowprops=dict(arrowstyle="->", color=COLORS["dark"], linewidth=0.85),
        fontsize=7.2,
        color=COLORS["dark"],
        ha="center",
        va="center",
    )
    style_axis(
        ax,
        r"Ion concentration, $c_{\mathrm{ion}}$ (M)",
        r"$\phi_{\mathrm{RP}}$ (mV)",
        r"At fixed $C_{\mathrm{H}}=0.20$ F/m$^2$",
    )


def plot_heatmap(ax: plt.Axes) -> None:
    c_h_mesh, c_ion_mesh = np.meshgrid(C_H_GRID, C_ION_GRID_M)
    phi, _g, _lambda_d = phi_rp_formula(c_h_mesh, c_ion_mesh)
    mesh = ax.pcolormesh(C_H_GRID, C_ION_GRID_M, 1000.0 * phi, shading="auto", cmap="viridis")
    ax.contour(
        C_H_GRID,
        C_ION_GRID_M,
        1000.0 * phi,
        levels=[-160, -120, -80, -40, -20],
        colors="white",
        linewidths=0.65,
        alpha=0.82,
    )
    ax.axvline(FIXED_C_H, color="white", linestyle=(0, (3, 2)), linewidth=0.9)
    ax.axhline(FIXED_C_ION_M, color="white", linestyle=(0, (3, 2)), linewidth=0.9)
    ax.scatter([FIXED_C_H], [FIXED_C_ION_M], color="#F26B38", edgecolor="white", linewidth=0.7, s=34, zorder=5)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(float(C_H_GRID[0]), float(C_H_GRID[-1]))
    ax.set_ylim(float(C_ION_GRID_M[0]), float(C_ION_GRID_M[-1]))
    style_axis(
        ax,
        r"$C_{\mathrm{H}}$ (F/m$^2$)",
        r"$c_{\mathrm{ion}}$ (M)",
        r"Two controls of $\phi_{\mathrm{RP}}$",
    )
    cbar = ax.figure.colorbar(mesh, ax=ax, pad=0.015, fraction=0.047)
    cbar.set_label(r"$\phi_{\mathrm{RP}}$ (mV)")
    cbar.ax.tick_params(length=2.8, width=0.8, labelsize=7.5)


def save_figure(fig: plt.Figure, stem: str) -> list[Path]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for ext in ("png", "svg"):
        path = OUT_DIR / f"{stem}_{TAG}.{ext}"
        fig.savefig(path, dpi=500, bbox_inches="tight")
        paths.append(path)
    plt.close(fig)
    return paths


def make_single_figures(ch_rows: list[dict[str, float]], cion_rows: list[dict[str, float]]) -> list[Path]:
    saved: list[Path] = []

    fig, ax = plt.subplots(figsize=(3.35, 2.65))
    plot_ch_sweep(ax, ch_rows)
    saved.extend(save_figure(fig, "phi_rp_CH_sweep"))

    fig, ax = plt.subplots(figsize=(3.35, 2.65))
    plot_cion_sweep(ax, cion_rows)
    saved.extend(save_figure(fig, "phi_rp_cion_sweep"))

    fig, ax = plt.subplots(figsize=(3.45, 2.85))
    plot_heatmap(ax)
    saved.extend(save_figure(fig, "phi_rp_CH_cion_heatmap"))

    return saved


def make_combined_figure(ch_rows: list[dict[str, float]], cion_rows: list[dict[str, float]]) -> list[Path]:
    fig, axes = plt.subplots(1, 3, figsize=(8.45, 2.75), gridspec_kw={"width_ratios": [1.0, 1.0, 1.12]})
    plot_ch_sweep(axes[0], ch_rows)
    plot_cion_sweep(axes[1], cion_rows)
    plot_heatmap(axes[2])
    fig.suptitle(
        r"Homogeneous surface, $E=0.40$ V $<$ PZC $=0.60$ V",
        x=0.02,
        ha="left",
        fontsize=10.2,
    )
    fig.subplots_adjust(left=0.07, right=0.985, bottom=0.23, top=0.82, wspace=0.42)
    return save_figure(fig, "phi_rp_CH_cion_explanation")


def validate_homogeneous_limit(rows: list[dict[str, float]]) -> None:
    for row in rows:
        spread = abs(row["phi_RP_max_V"] - row["phi_RP_min_V"])
        if spread > 1.0e-12:
            raise ValueError(f"Homogeneous phi_RP is not spatially constant; spread={spread:.3g}")
        err = abs(row["phi_RP_V"] - row["phi_RP_formula_V"])
        if err > 1.0e-12:
            raise ValueError(f"Numeric/formula phi_RP mismatch; err={err:.3g}")


def main() -> None:
    apply_style()
    CSV_DIR.mkdir(parents=True, exist_ok=True)
    save_inputs()

    ch_rows, cion_rows, heatmap_rows = build_data()
    validate_homogeneous_limit(ch_rows + cion_rows)
    write_csv(CSV_DIR / f"phi_rp_CH_sweep_{TAG}.csv", ch_rows)
    write_csv(CSV_DIR / f"phi_rp_cion_sweep_{TAG}.csv", cion_rows)
    write_csv(CSV_DIR / f"phi_rp_CH_cion_heatmap_{TAG}.csv", heatmap_rows)

    saved = []
    saved.extend(make_single_figures(ch_rows, cion_rows))
    saved.extend(make_combined_figure(ch_rows, cion_rows))
    for path in saved:
        print(f"Saved {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
