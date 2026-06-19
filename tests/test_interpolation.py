import unittest

from yield_curve_interpolation_lab.curve import CurveInput, InterpolationMode, YieldCurve
from yield_curve_interpolation_lab.experiments import DEFAULT_CURVE_INPUT, build_curves
from yield_curve_interpolation_lab.swap import PlainSwap, par_swap_rate


class InterpolationTests(unittest.TestCase):
    def test_discount_factors_are_decreasing(self) -> None:
        for curve in build_curves(DEFAULT_CURVE_INPUT).values():
            last = 1.0
            for maturity in [0.25 * i for i in range(1, 41)]:
                current = curve.discount_factor(maturity)
                self.assertLessEqual(current, last + 1.0e-12)
                last = current

    def test_par_swap_has_near_zero_pv(self) -> None:
        for curve in build_curves(DEFAULT_CURVE_INPUT).values():
            par = par_swap_rate(curve, maturity=5.0, period_length=0.5)
            swap = PlainSwap(maturity=5.0, period_length=0.5, fixed_rate=par)
            self.assertLess(abs(swap.present_value(curve)), 1.0e-6)

    def test_interpolation_modes_differ_off_grid(self) -> None:
        curves = build_curves(DEFAULT_CURVE_INPUT)
        values = [curves[name].forward_rate(5.25, 5.50) for name in curves]
        self.assertGreater(max(values) - min(values), 1.0e-4)


if __name__ == "__main__":
    unittest.main()
