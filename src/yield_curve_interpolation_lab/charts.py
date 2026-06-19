from __future__ import annotations

from pathlib import Path


def write_multi_line_chart_svg(
    *,
    title: str,
    subtitle: str,
    x_values: list[float],
    series: dict[str, list[float]],
    output_path: Path,
) -> None:
    colors = {
        "LINEAR_ZERO_RATES": "#61D9FF",
        "LOG_LINEAR_DISCOUNT_FACTORS": "#7CF0C5",
        "LINEAR_DISCOUNT_FACTORS": "#FFC86E",
    }
    width, height = 1500, 920
    left, right, top, bottom = 140, 1350, 200, 780
    chart_width = right - left
    chart_height = bottom - top
    y_values = [value for values in series.values() for value in values]
    y_min, y_max = min(y_values), max(y_values)
    y_span = max(y_max - y_min, 1.0e-8)
    y_min -= 0.08 * y_span
    y_max += 0.10 * y_span
    y_span = y_max - y_min
    x_min, x_max = min(x_values), max(x_values)

    def px(x: float) -> float:
        return left + (x - x_min) / (x_max - x_min) * chart_width

    def py(y: float) -> float:
        return bottom - (y - y_min) / y_span * chart_height

    svg = [
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg">',
        '<rect width="1500" height="920" rx="28" fill="#0B1220"/>',
        f'<text x="{left}" y="108" fill="#F5F7FB" font-size="40" font-weight="700" font-family="SF Pro Display, Helvetica, Arial, sans-serif">{title}</text>',
        f'<text x="{left}" y="146" fill="#91A4BD" font-size="18" font-family="SF Pro Text, Helvetica, Arial, sans-serif">{subtitle}</text>',
        f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="#32455E" stroke-width="2"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" stroke="#32455E" stroke-width="2"/>',
    ]
    legend_x = 960
    for offset, name in enumerate(series):
        svg.append(f'<rect x="{legend_x}" y="{84 + offset * 28}" width="18" height="18" rx="4" fill="{colors[name]}"/>')
        svg.append(f'<text x="{legend_x + 32}" y="{99 + offset * 28}" fill="#DDE8F4" font-size="16" font-family="SF Pro Text, Helvetica, Arial, sans-serif">{name}</text>')

    for grid in range(5):
        y = bottom - chart_height * grid / 4
        value = y_min + y_span * grid / 4
        svg.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="#1B2B40" stroke-width="1"/>')
        svg.append(f'<text x="40" y="{y + 6:.1f}" fill="#7890AA" font-size="16" font-family="SF Pro Text, Helvetica, Arial, sans-serif">{100 * value:.2f}%</text>')

    for marker in (1.0, 2.0, 3.0, 5.0, 7.0, 10.0):
        x = px(marker)
        svg.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{bottom}" stroke="#132338" stroke-width="1"/>')
        svg.append(f'<text x="{x - 15:.1f}" y="820" fill="#AABED6" font-size="15" font-family="SF Pro Text, Helvetica, Arial, sans-serif">{marker:.0f}Y</text>')

    for name, values in series.items():
        path = " ".join(
            ("M" if index == 0 else "L") + f" {px(x):.2f} {py(y):.2f}"
            for index, (x, y) in enumerate(zip(x_values, values))
        )
        svg.append(f'<path d="{path}" stroke="{colors[name]}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')

    svg.append("</svg>")
    output_path.write_text("\n".join(svg), encoding="utf-8")


def write_grouped_bar_chart_svg(
    *,
    title: str,
    subtitle: str,
    categories: list[str],
    series: dict[str, list[float]],
    output_path: Path,
) -> None:
    colors = ["#61D9FF", "#7CF0C5", "#FFC86E"]
    width, height = 1500, 920
    left, right, top, bottom = 150, 1350, 200, 780
    chart_width = right - left
    chart_height = bottom - top
    maximum = max(value for values in series.values() for value in values) * 1.12
    category_width = chart_width / max(len(categories), 1)
    bar_width = min(72.0, category_width * 0.22)

    svg = [
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg">',
        '<rect width="1500" height="920" rx="28" fill="#0B1220"/>',
        f'<text x="{left}" y="108" fill="#F5F7FB" font-size="40" font-weight="700" font-family="SF Pro Display, Helvetica, Arial, sans-serif">{title}</text>',
        f'<text x="{left}" y="146" fill="#91A4BD" font-size="18" font-family="SF Pro Text, Helvetica, Arial, sans-serif">{subtitle}</text>',
        f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="#32455E" stroke-width="2"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" stroke="#32455E" stroke-width="2"/>',
    ]

    names = list(series.keys())
    legend_x = 960
    for index, name in enumerate(names):
        svg.append(f'<rect x="{legend_x}" y="{84 + index * 28}" width="18" height="18" rx="4" fill="{colors[index]}"/>')
        svg.append(f'<text x="{legend_x + 32}" y="{99 + index * 28}" fill="#DDE8F4" font-size="16" font-family="SF Pro Text, Helvetica, Arial, sans-serif">{name}</text>')

    for grid in range(5):
        y = bottom - chart_height * grid / 4
        value = maximum * grid / 4
        svg.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="#1B2B40" stroke-width="1"/>')
        svg.append(f'<text x="40" y="{y + 6:.1f}" fill="#7890AA" font-size="16" font-family="SF Pro Text, Helvetica, Arial, sans-serif">{100 * value:.2f}%</text>')

    for category_index, category in enumerate(categories):
        center = left + category_width * (category_index + 0.5)
        for series_index, name in enumerate(names):
            value = series[name][category_index]
            x = center + (series_index - 1) * (bar_width + 10) - bar_width / 2
            h = chart_height * value / maximum
            y = bottom - h
            svg.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{h:.1f}" rx="12" fill="{colors[series_index]}"/>')
            svg.append(f'<text x="{x - 6:.1f}" y="{y - 10:.1f}" fill="#DDE8F4" font-size="14" font-family="SF Pro Text, Helvetica, Arial, sans-serif">{100 * value:.2f}%</text>')
        svg.append(f'<text x="{center - 38:.1f}" y="820" fill="#AABED6" font-size="15" font-family="SF Pro Text, Helvetica, Arial, sans-serif">{category}</text>')

    svg.append("</svg>")
    output_path.write_text("\n".join(svg), encoding="utf-8")
