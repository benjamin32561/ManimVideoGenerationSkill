"""Welch Labs components, ported from github.com/stephencwelch/manim_videos (MIT).

A component is ``name(spec, kit) -> Mobject``: it reads canvas pixels and palette tokens from
its layout entry and places itself. Sources in ``vendor/welch-labs-videos/``:

* ``custom/welch_axes.py``          nice 1-2-5 ticks, brown axes with outward ticks
* ``custom/welch_tip_manimce.py``   the notched arrowhead
* ``_2025/backprop_2/p22_24.py``    fixed-width number formatting
"""

import math

import manimgx as m
import numpy as np

from explain.objects import Kit

TIP_POINTS = ((32.33, 13.21), (0.0, 26.42), (7.67, 13.21), (0.0, 0.0))
TIP_LENGTH = 32.33
TICK_STEPS = (1.0, 0.5, 0.2, 0.1)


def nice_ticks(low: float, high: float, min_ticks: int = 3, max_ticks: int = 10) -> list[float]:
    """Tick values on a 1-2-5 grid between two values (Welch's ``generate_nice_ticks``).

    Args:
        low: Smallest value the axis shows.
        high: Largest value the axis shows.
        min_ticks: Fewest ticks wanted.
        max_ticks: Most ticks wanted.

    Returns:
        Tick values from ``low`` to ``high``, at the coarsest step that gives at least
        ``min_ticks`` ticks without exceeding ``max_ticks``.
    """
    power = math.floor(math.log10(high - low))
    ticks: list[float] = []
    for factor in TICK_STEPS:
        step = factor * 10 ** power
        first = math.ceil(low / step - 1e-9) * step
        ticks = [round(first + k * step, 10) for k in range(int((high - first) / step + 1e-9) + 1)]
        if min_ticks <= len(ticks) <= max_ticks:
            return ticks
    return ticks


def format_number(value: float | int, width: int = 6) -> str:
    """A number at a precision set by its size, right-justified to a fixed width.

    Updating readouts keep their place instead of jittering (Welch's ``format_number``). An
    ``int`` is a count and shows no decimals.

    Args:
        value: The number (an ``int`` for counts).
        width: Characters to pad to.

    Returns:
        ``15`` for a count; otherwise ``123``, ``12.3`` or ``1.23`` style text; padded on the
        left.
    """
    if isinstance(value, int):
        return str(value).rjust(width)
    size = abs(value)
    text = f"{value:.0f}" if size >= 100 else f"{value:.1f}" if size >= 10 else f"{value:.2f}"
    return text.rjust(width)


def notched_tip(kit: Kit, at: list[float], angle: float, length_px: float, color: str) -> m.Mobject:
    """The Welch arrowhead: a notched dart with its point at ``at``.

    Args:
        kit: Unit conversion and builders.
        at: ``[x, y]`` of the point (px).
        angle: Direction it points, in radians, measured on screen (0 = right, π/2 = up).
        length_px: Its length (px).
        color: Palette token.

    Returns:
        The filled tip.
    """
    scale = length_px / TIP_LENGTH
    corners = [kit.pt(at[0] + (px - TIP_LENGTH) * scale, at[1] - (py - TIP_POINTS[1][1] / 2) * scale)
               for px, py in TIP_POINTS]
    tip = m.Polygon(*corners, fill_color=kit.color(color), fill_opacity=1.0, stroke_width=0)
    return tip.rotate(angle, about_point=kit.pt(*at))


def arrow(spec: dict, kit: Kit) -> m.Mobject:
    """A straight arrow with the notched tip.

    Fields:
        points: ``[tail, head]`` in px.
        stroke: Colour token, default ``brown``.
        stroke_width: Shaft width (px), default 3.
        tip_px: Tip length (px), default 18.

    Args:
        spec: The layout entry.
        kit: Unit conversion and builders.

    Returns:
        A VGroup of shaft and tip.
    """
    (x0, y0), (x1, y1) = spec["points"]
    color, width, tip = spec.get("stroke", "brown"), spec.get("stroke_width", 3), spec.get("tip_px", 18)
    angle = math.atan2(y0 - y1, x1 - x0)
    back = [x1 - tip * 0.7 * math.cos(angle), y1 + tip * 0.7 * math.sin(angle)]
    return m.VGroup(kit.polyline([[x0, y0], back], color, width), notched_tip(kit, [x1, y1], angle, tip, color))


def axes(spec: dict, kit: Kit) -> m.Mobject:
    """Welch axes: brown, ticks pointing outward, tick labels in math, notched tips.

    Fields:
        x0, y0, x1, y1: The plot rectangle (px); axes run along its left and bottom edges.
        x_range, y_range: ``[low, high]`` values at the rectangle's edges.
        x_ticks, y_ticks: Tick values; default ``nice_ticks`` of each range.
        color: Colour token, default ``brown``.
        label_size: Tick-label size (px or role), default ``tick``.

    Args:
        spec: The layout entry.
        kit: Unit conversion and builders.

    Returns:
        A VGroup of both axes with ticks and labels.
    """
    x0, y0, x1, y1 = spec["x0"], spec["y0"], spec["x1"], spec["y1"]
    (xl, xh), (yl, yh) = spec["x_range"], spec["y_range"]
    color, size = spec.get("color", "brown"), spec.get("label_size", "tick")
    tick, gap = 10, kit.size_px(size) * 0.9
    parts: list[m.Mobject] = [
        arrow({"points": [[x0, y1], [x1 + 24, y1]], "stroke": color}, kit),
        arrow({"points": [[x0, y1], [x0, y0 - 24]], "stroke": color}, kit),
    ]
    for value in spec.get("x_ticks") or nice_ticks(xl, xh):
        x = x0 + (x1 - x0) * (value - xl) / (xh - xl)
        parts.append(kit.polyline([[x, y1], [x, y1 + tick]], color, 2))
        parts.append(kit.place(kit.math([f"{value:g}"], size, color), x, y1 + tick + gap))
    for value in spec.get("y_ticks") or nice_ticks(yl, yh):
        y = y1 - (y1 - y0) * (value - yl) / (yh - yl)
        parts.append(kit.polyline([[x0 - tick, y], [x0, y]], color, 2))
        parts.append(kit.place(kit.math([f"{value:g}"], size, color), x0 - tick - 8, y, "right"))
    return m.VGroup(*parts)


def number(spec: dict, kit: Kit) -> m.Mobject:
    """A fixed-width numeric readout, right-aligned so changing values keep their place.

    Fields:
        value: The number; an integer (``15``) shows as a count, without decimals.
        x, y: Right edge and vertical centre (px).
        size: Px or role, default ``label``.
        color: Colour token, default ``tan``.
        unit: Optional LaTeX after the number (e.g. ``\\,\\text{mV}``).

    Args:
        spec: The layout entry.
        kit: Unit conversion and builders.

    Returns:
        The readout.
    """
    text = format_number(spec["value"]).strip() + spec.get("unit", "")
    mob = kit.math([text], spec.get("size", "label"), spec.get("color", "tan"))
    return kit.place(mob, spec["x"], spec["y"], "right")


def heatmap(spec: dict, kit: Kit) -> m.Mobject:
    """A grid of coloured cells, Welch's way of showing weights and activations.

    Diverging maps run cyan (negative) through black to magenta (positive); sequential maps
    run black to yellow.

    Fields:
        x0, y0: Top-left corner (px).
        cell_px: Cell size (px).
        values: Rows of numbers.
        scale: The value shown at full colour (default: the largest absolute value).
        palette: ``diverging`` (default) or ``sequential``.
        gap_px: Space between cells (px), default 2.

    Args:
        spec: The layout entry.
        kit: Unit conversion and builders.

    Returns:
        A VGroup of cells, row by row.
    """
    values = np.array(spec["values"], dtype=float)
    scale = float(spec.get("scale") or np.abs(values).max() or 1.0)
    cell, gap = spec["cell_px"], spec.get("gap_px", 2)
    diverging = spec.get("palette", "diverging") == "diverging"
    low, high = ("cyan", "magenta") if diverging else ("black", "yellow")
    cells = []
    for r, row in enumerate(values):
        for c, v in enumerate(row):
            share = max(-1.0, min(1.0, v / scale))
            color = m.interpolate_color(m.BLACK, kit.color(high if share >= 0 else low), abs(share)) \
                if diverging else m.interpolate_color(m.BLACK, kit.color(high), max(share, 0.0))
            x, y = spec["x0"] + c * (cell + gap), spec["y0"] + r * (cell + gap)
            cells.append(m.Square(side_length=kit.units(cell), fill_color=color, fill_opacity=1.0,
                                  stroke_width=0).move_to(kit.pt(x + cell / 2, y + cell / 2)))
    return m.VGroup(*cells)
