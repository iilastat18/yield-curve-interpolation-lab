from __future__ import annotations

from dataclasses import dataclass

from .curve import YieldCurve


@dataclass(frozen=True)
class PlainSwap:
    maturity: float
    period_length: float
    fixed_rate: float
    notional: float = 1_000_000.0

    def present_value(self, curve: YieldCurve) -> float:
        pv = 0.0
        period_start = 0.0
        while period_start < self.maturity - 1.0e-12:
            period_end = min(self.maturity, period_start + self.period_length)
            accrual = period_end - period_start
            pv += (
                self.notional
                * (curve.forward_rate(period_start, period_end) - self.fixed_rate)
                * accrual
                * curve.discount_factor(period_end)
            )
            period_start = period_end
        return pv


def par_swap_rate(curve: YieldCurve, *, maturity: float, period_length: float) -> float:
    floating_leg = 0.0
    fixed_annuity = 0.0
    period_start = 0.0
    while period_start < maturity - 1.0e-12:
        period_end = min(maturity, period_start + period_length)
        accrual = period_end - period_start
        floating_leg += curve.discount_factor(period_start) - curve.discount_factor(period_end)
        fixed_annuity += accrual * curve.discount_factor(period_end)
        period_start = period_end
    return floating_leg / fixed_annuity
