from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
SAME_LENGTH_I0_ALPHA_DIR = ROOT / "Figures" / "Figure_same_length_i0_alpha"
sys.path.insert(0, str(SAME_LENGTH_I0_ALPHA_DIR))

import same_length_i0_alpha_common as common  # noqa: E402


solver = common.solver

SCAN_DIR = ROOT / "Figures" / "Figure_scan"
FIG_DIR = SCAN_DIR / "figures"
CSV_DIR = SCAN_DIR / "csv"
INPUTS_DIR = SCAN_DIR / "inputs"

EXPECTED_OFAT_PARAM_COUNT = 22
EXPECTED_PNG_COUNT = EXPECTED_OFAT_PARAM_COUNT * 3 + 2


def ensure_dirs() -> None:
    for path in (SCAN_DIR, FIG_DIR, CSV_DIR, INPUTS_DIR):
        path.mkdir(parents=True, exist_ok=True)


def remove_previous_generated_outputs() -> None:
    for pattern in (
        "ofat_compare_*.png",
        "heatmap_combined_panel_*.png",
        "*.svg",
        "*.pdf",
    ):
        for path in FIG_DIR.glob(pattern):
            path.unlink()

    for pattern in (
        "ofat_compare_*.csv",
        "heatmap_compare_*.csv",
        "results_summary.csv",
        "summary_compare.csv",
        "summary_compare.json",
    ):
        for path in CSV_DIR.glob(pattern):
            path.unlink()


def save_traceability_inputs(params: dict[str, Any], summary: dict[str, str]) -> None:
    with (SCAN_DIR / "params.json").open("w", encoding="utf-8") as f:
        json.dump(params, f, indent=2, sort_keys=True)
        f.write("\n")

    with (INPUTS_DIR / f"params_{common.OUTPUT_TAG}.json").open("w", encoding="utf-8") as f:
        json.dump(params, f, indent=2, sort_keys=True)
        f.write("\n")
    with (INPUTS_DIR / f"overrides_{common.OUTPUT_TAG}.json").open("w", encoding="utf-8") as f:
        json.dump(common.PARAM_OVERRIDES, f, indent=2, sort_keys=True)
        f.write("\n")
    with (INPUTS_DIR / f"summary_compare_{common.OUTPUT_TAG}.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
        f.write("\n")

    summary_df = pd.DataFrame([summary])
    summary_df.to_csv(INPUTS_DIR / f"summary_compare_{common.OUTPUT_TAG}.csv", index=False)
    summary_df.to_csv(CSV_DIR / "summary_compare.csv", index=False)
    with (CSV_DIR / "summary_compare.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
        f.write("\n")


def baseline_summary_rows(params: dict[str, Any], pair: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        solver.make_summary_row(
            "baseline:with_edl_FULL",
            params,
            pair["with_edl"],
            extra={"use_edl_case": "with_edl_FULL"},
        ),
        solver.make_summary_row(
            "baseline:without_edl",
            params,
            pair["no_edl"],
            extra={"use_edl_case": "without_edl"},
        ),
    ]


def plot_single_metric_ofat_pngs(params: dict[str, Any]) -> None:
    specs = solver.make_ofat_specs(params)
    if len(specs) != EXPECTED_OFAT_PARAM_COUNT:
        raise RuntimeError(f"Expected {EXPECTED_OFAT_PARAM_COUNT} OFAT params, got {len(specs)}")

    for pname, spec in specs.items():
        csv_path = CSV_DIR / f"ofat_compare_{pname}.csv"
        if not csv_path.is_file():
            raise RuntimeError(f"Missing OFAT CSV: {csv_path}")
        dfp = pd.read_csv(csv_path)

        solver._plot_ofat_edl_comparison(
            dfp,
            pname,
            with_col="E_mix_with_edl_FULL",
            no_col="E_mix_without_edl",
            metric_label="E_mix",
            ylab=solver._plot_axis_label("E_mix"),
            spec_type=spec["type"],
            fig_dir=FIG_DIR,
        )
        solver._plot_ofat_edl_comparison(
            dfp,
            pname,
            with_col="i_mix_avg_with_edl_FULL_A_per_m2",
            no_col="i_mix_avg_without_edl_A_per_m2",
            metric_label="i_mix_avg_A_per_m2",
            ylab=solver._plot_axis_label("i_mix_avg"),
            spec_type=spec["type"],
            fig_dir=FIG_DIR,
            y_axis_key="i_mix_avg",
        )


def assert_outputs() -> list[Path]:
    pngs = sorted(FIG_DIR.glob("*.png"))
    svgs = sorted(SCAN_DIR.glob("**/*.svg"))
    pdfs = sorted(SCAN_DIR.glob("**/*.pdf"))
    if len(pngs) != EXPECTED_PNG_COUNT:
        raise RuntimeError(f"Expected {EXPECTED_PNG_COUNT} PNG outputs, got {len(pngs)}")
    if svgs:
        raise RuntimeError(f"Expected zero SVG outputs in {SCAN_DIR}, found {len(svgs)}")
    if pdfs:
        raise RuntimeError(f"Expected zero PDF outputs in {SCAN_DIR}, found {len(pdfs)}")

    expected = [
        FIG_DIR / "heatmap_combined_panel_log.png",
        FIG_DIR / "heatmap_combined_panel_linear.png",
    ]
    missing = [path for path in expected if not path.is_file() or path.stat().st_size == 0]
    if missing:
        raise RuntimeError(f"Missing heatmap PNG outputs: {missing}")
    return pngs


def main() -> None:
    ensure_dirs()
    remove_previous_generated_outputs()

    params = common.load_same_length_i0_alpha_params()
    pair = solver.run_edl_comparison_pair(params, mode="FULL")
    summary = common.summary_from_pair(pair)
    common.validate_same_length_i0_alpha_params(params)
    common.assert_expected_values(summary)
    save_traceability_inputs(params, summary)

    summary_rows = baseline_summary_rows(params, pair)

    print(f"Building scan figures for {common.OUTPUT_TAG}")
    print(f"Output directory: {FIG_DIR.relative_to(ROOT)}")

    print("Running OFAT scans")
    solver.run_ofat(params, out_dir=SCAN_DIR, summary_rows=summary_rows)
    plot_single_metric_ofat_pngs(params)

    print("Running combined heatmap scans")
    solver.run_heatmaps(params, out_dir=SCAN_DIR, summary_rows=summary_rows)

    pd.DataFrame(summary_rows).to_csv(CSV_DIR / "results_summary.csv", index=False)

    pngs = assert_outputs()
    print(f"Verified {len(pngs)} PNG outputs, zero SVG outputs, and zero PDF outputs")
    for path in pngs:
        print(f"  {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
