from __future__ import annotations

import csv
import json
from pathlib import Path

from .charts import write_grouped_bar_chart_svg, write_multi_line_chart_svg
from .curve import CurveInput, InterpolationMode, YieldCurve
from .swap import PlainSwap, par_swap_rate


DEFAULT_CURVE_INPUT = CurveInput(
    times=(1.0, 2.0, 3.0, 5.0, 7.0, 10.0),
    zero_rates=(0.0220, 0.0270, 0.0310, 0.0340, 0.0330, 0.0360),
)


def build_curves(curve_input: CurveInput = DEFAULT_CURVE_INPUT) -> dict[str, YieldCurve]:
    curve_input.validate()
    return {
        mode.value: YieldCurve(curve_input=curve_input, interpolation_mode=mode)
        for mode in InterpolationMode
    }


def write_results_bundle(*, output_root: Path, curve_input: CurveInput = DEFAULT_CURVE_INPUT) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    curves = build_curves(curve_input)
    grid = [round(0.25 * index, 2) for index in range(1, 41)]
    curve_rows: list[dict[str, str]] = []

    zero_series = {name: [] for name in curves}
    forward_series = {name: [] for name in curves}
    for maturity in grid:
        row = {"maturity": f"{maturity:.2f}"}
        for name, curve in curves.items():
            zero = curve.zero_rate(maturity)
            forward = curve.forward_rate(max(maturity - 0.25, 0.0), maturity)
            row[f"{name}_zero_rate"] = f"{zero:.8f}"
            row[f"{name}_forward_rate"] = f"{forward:.8f}"
            zero_series[name].append(zero)
            forward_series[name].append(forward)
        curve_rows.append(row)
    _write_csv(output_root / "curve_grid.csv", curve_rows)

    summary_rows = []
    par_categories = ["5Y par swap", "7Y par swap", "6.5Y target coupon"]
    par_series = {name: [] for name in curves}
    for name, curve in curves.items():
        par_5y = par_swap_rate(curve, maturity=5.0, period_length=0.5)
        par_7y = par_swap_rate(curve, maturity=7.0, period_length=0.5)
        target_coupon = 0.0350
        target_swap = PlainSwap(maturity=6.5, period_length=0.5, fixed_rate=target_coupon)
        target_pv = target_swap.present_value(curve)
        avg_forward = sum(curve.forward_rate(t - 0.25, t) for t in (5.25, 5.50, 5.75, 6.0)) / 4.0
        summary_rows.append(
            {
                "mode": name,
                "par_swap_5y": f"{par_5y:.8f}",
                "par_swap_7y": f"{par_7y:.8f}",
                "avg_forward_5_to_6y": f"{avg_forward:.8f}",
                "target_swap_pv": f"{target_pv:.2f}",
            }
        )
        par_series[name] = [par_5y, par_7y, avg_forward]
    _write_csv(output_root / "pricing_summary.csv", summary_rows)
    (output_root / "pricing_summary.json").write_text(json.dumps(summary_rows, indent=2), encoding="utf-8")

    write_multi_line_chart_svg(
        title="Forward Curve Comparison",
        subtitle="Interpolation changes the shape between quoted nodes, especially in the 4Y to 8Y region.",
        x_values=grid,
        series=forward_series,
        output_path=output_root / "forward_curve_comparison.svg",
    )
    write_grouped_bar_chart_svg(
        title="Par Rate And Local Forward Comparison",
        subtitle="The same market nodes imply slightly different swap and forward metrics once interpolation changes.",
        categories=par_categories,
        series=par_series,
        output_path=output_root / "par_rate_comparison.svg",
    )


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
