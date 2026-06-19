from __future__ import annotations

from dataclasses import dataclass
import enum
import math


class InterpolationMode(str, enum.Enum):
    LINEAR_ZERO_RATES = "LINEAR_ZERO_RATES"
    LOG_LINEAR_DISCOUNT_FACTORS = "LOG_LINEAR_DISCOUNT_FACTORS"
    LINEAR_DISCOUNT_FACTORS = "LINEAR_DISCOUNT_FACTORS"


@dataclass(frozen=True)
class CurveInput:
    times: tuple[float, ...]
    zero_rates: tuple[float, ...]

    def validate(self) -> None:
        if len(self.times) != len(self.zero_rates) or not self.times:
            raise ValueError("Curve times and rates must have the same positive length.")
        previous = 0.0
        for time in self.times:
            if time <= previous:
                raise ValueError("Curve times must be strictly increasing.")
            previous = time


@dataclass(frozen=True)
class YieldCurve:
    curve_input: CurveInput
    interpolation_mode: InterpolationMode

    def discount_factor(self, maturity: float) -> float:
        if maturity < 0.0:
            raise ValueError("Maturity cannot be negative.")
        if maturity == 0.0:
            return 1.0

        if self.interpolation_mode == InterpolationMode.LINEAR_ZERO_RATES:
            return math.exp(-self._interpolate_zero_rate(maturity) * maturity)
        if self.interpolation_mode == InterpolationMode.LOG_LINEAR_DISCOUNT_FACTORS:
            return math.exp(self._interpolate_log_discount(maturity))
        if self.interpolation_mode == InterpolationMode.LINEAR_DISCOUNT_FACTORS:
            return self._interpolate_discount_factor(maturity)

        raise ValueError(f"Unsupported interpolation mode: {self.interpolation_mode}")

    def zero_rate(self, maturity: float) -> float:
        if maturity == 0.0:
            return self.curve_input.zero_rates[0]
        return -math.log(self.discount_factor(maturity)) / maturity

    def forward_rate(self, period_start: float, period_end: float) -> float:
        if period_end <= period_start:
            raise ValueError("Forward period end must be strictly larger than period start.")
        df_start = self.discount_factor(period_start)
        df_end = self.discount_factor(period_end)
        return (df_start / df_end - 1.0) / (period_end - period_start)

    def _interpolate_zero_rate(self, maturity: float) -> float:
        times, rates = self.curve_input.times, self.curve_input.zero_rates
        if maturity <= times[0]:
            return rates[0]
        if maturity >= times[-1]:
            return rates[-1]
        for index in range(1, len(times)):
            if maturity <= times[index]:
                return _linear_interpolate(maturity, times[index - 1], rates[index - 1], times[index], rates[index])
        raise RuntimeError("Linear zero interpolation failed.")

    def _interpolate_log_discount(self, maturity: float) -> float:
        times, rates = self.curve_input.times, self.curve_input.zero_rates
        if maturity <= times[0]:
            return _linear_interpolate(maturity, 0.0, 0.0, times[0], -rates[0] * times[0])
        if maturity >= times[-1]:
            return -rates[-1] * maturity
        for index in range(1, len(times)):
            if maturity <= times[index]:
                left_value = -rates[index - 1] * times[index - 1]
                right_value = -rates[index] * times[index]
                return _linear_interpolate(maturity, times[index - 1], left_value, times[index], right_value)
        raise RuntimeError("Log-linear interpolation failed.")

    def _interpolate_discount_factor(self, maturity: float) -> float:
        times, rates = self.curve_input.times, self.curve_input.zero_rates
        discounts = [math.exp(-rate * time) for time, rate in zip(times, rates)]
        if maturity <= times[0]:
            return _linear_interpolate(maturity, 0.0, 1.0, times[0], discounts[0])
        if maturity >= times[-1]:
            tail_rate = rates[-1]
            return discounts[-1] * math.exp(-tail_rate * (maturity - times[-1]))
        for index in range(1, len(times)):
            if maturity <= times[index]:
                return _linear_interpolate(
                    maturity,
                    times[index - 1],
                    discounts[index - 1],
                    times[index],
                    discounts[index],
                )
        raise RuntimeError("Linear discount interpolation failed.")


def _linear_interpolate(x: float, x0: float, y0: float, x1: float, y1: float) -> float:
    if x1 == x0:
        return y0
    weight = (x - x0) / (x1 - x0)
    return y0 + weight * (y1 - y0)
