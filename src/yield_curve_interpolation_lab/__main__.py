from __future__ import annotations

from pathlib import Path

from .experiments import DEFAULT_CURVE_INPUT, build_curves, write_results_bundle
from .swap import PlainSwap, par_swap_rate


def main() -> None:
    output_root = Path(__file__).resolve().parents[2] / "results"
    write_results_bundle(output_root=output_root, curve_input=DEFAULT_CURVE_INPUT)

    print("Interpolation metrics:")
    for name, curve in build_curves(DEFAULT_CURVE_INPUT).items():
        par_5y = par_swap_rate(curve, maturity=5.0, period_length=0.5)
        par_7y = par_swap_rate(curve, maturity=7.0, period_length=0.5)
        target_pv = PlainSwap(maturity=6.5, period_length=0.5, fixed_rate=0.0350).present_value(curve)
        avg_forward = sum(curve.forward_rate(t - 0.25, t) for t in (5.25, 5.50, 5.75, 6.0)) / 4.0
        print(
            f"  {name}: par5y={100*par_5y:.4f}%, par7y={100*par_7y:.4f}%, "
            f"avg_forward_5to6y={100*avg_forward:.4f}%, target_pv={target_pv:.2f}"
        )
    print(f"\nResults written to: {output_root}")


if __name__ == "__main__":
    main()
