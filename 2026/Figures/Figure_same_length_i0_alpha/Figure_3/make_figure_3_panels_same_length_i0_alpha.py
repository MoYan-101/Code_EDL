from __future__ import annotations

import copy
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
SAME_LENGTH_I0_ALPHA_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SAME_LENGTH_I0_ALPHA_DIR))

import same_length_i0_alpha_common as common  # noqa: E402
from Figures.Figure_3 import make_figure_3_panels as base  # noqa: E402


def plot_panel_c_same_length_i0_alpha(data: Any) -> list[Path]:
    fig, ax = base.make_single_axis_panel()
    ax.plot(
        data.x_nm,
        data.c_r1_norm,
        color=base.COLORS["with"],
        linewidth=2.0,
        label=r"$C_{\mathrm{Red},1}/C_{\mathrm{bulk}}$ (with EDL)",
        zorder=3,
    )
    ax.plot(
        data.x_nm,
        data.c_o2_norm,
        color=base.COLORS["with_gold"],
        linewidth=2.0,
        label=r"$C_{\mathrm{Ox},2}/C_{\mathrm{bulk}}$ (with EDL)",
        zorder=3,
    )
    ax.plot(
        data.x_nm,
        base.np.ones_like(data.x_nm),
        color=base.COLORS["without"],
        linewidth=1.6,
        linestyle=(0, (4, 2)),
        label="without EDL",
        zorder=2,
    )
    base.add_boundaries(ax, data)
    ax.set_yscale("log")
    positive = base.np.concatenate(
        [
            data.c_r1_norm[base.np.isfinite(data.c_r1_norm) & (data.c_r1_norm > 0.0)],
            data.c_o2_norm[base.np.isfinite(data.c_o2_norm) & (data.c_o2_norm > 0.0)],
            base.np.array([1.0], dtype=float),
        ]
    )
    ax.set_ylim(float(base.np.min(positive)) / 1.25, float(base.np.max(positive)) * 30.0)
    base.style_axes(ax, "x (nm)", r"$c_i/c_{\mathrm{bulk}}$ (-)", "Local reactant concentration at RP")
    ax.legend(
        loc="upper right",
        fontsize=6.9,
        handlelength=1.7,
        ncols=1,
        borderaxespad=0.0,
    )
    return base.save_panel(fig, "figure_3_panel_c_local_reactant_concentration")


def main() -> None:
    common.ensure_output_dirs()
    params, summary = common.load_inputs_for_scripts()
    common.assert_expected_values(summary)

    def load_params() -> dict[str, Any]:
        return copy.deepcopy(params)

    def load_summary() -> dict[str, str]:
        return dict(summary)

    base.RESULT_ID = common.OUTPUT_TAG
    base.OUT_DIR = common.FIGURE_3_DIR
    base.load_params = load_params
    base.load_summary = load_summary
    base.plot_panel_c = plot_panel_c_same_length_i0_alpha
    base.PANEL_D_TITLE = "Local overpotential at RP"
    base.PANEL_E_TITLE = "Local current density at RP"
    base.PANEL_E_YMIN = -400.0
    base.main()


if __name__ == "__main__":
    main()
