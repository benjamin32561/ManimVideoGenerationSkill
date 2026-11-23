"""3Blue1Brown components: reusable objects for ``component`` layout entries.

A component is ``name(spec, kit) -> Mobject``. It reads its own fields from ``spec`` (canvas
pixels and palette tokens, like every layout object) and places itself.
"""

import manimgx as m

from explain.objects import Kit


def number_line(spec: dict, kit: Kit) -> m.Mobject:
    """A horizontal number line with ticks and math tick labels below them.

    Fields:
        x0, x1, y: The axis from ``x0`` to ``x1`` at height ``y`` (px).
        start, end, step: The value range and tick step.
        color: Axis and tick colour (palette token).
        label_color: Tick-label colour (palette token).
        label_size: Tick-label size (px or role), default ``tick``.
        tick_px: Tick length (px), default 16.
        stroke_width: Axis width (px), default 3.

    Args:
        spec: The layout entry.
        kit: Unit conversion and builders.

    Returns:
        A VGroup of the axis, the ticks and the labels.
    """
    x0, x1, y = spec["x0"], spec["x1"], spec["y"]
    start, end, step = spec["start"], spec["end"], spec["step"]
    tick = spec.get("tick_px", 16)
    width = spec.get("stroke_width", 3)
    axis = kit.polyline([[x0, y], [x1, y]], spec["color"], width)
    parts = [axis]
    count = round((end - start) / step)
    for i in range(count + 1):
        value = start + i * step
        x = x0 + (x1 - x0) * (value - start) / (end - start)
        parts.append(kit.polyline([[x, y - tick / 2], [x, y + tick / 2]], spec["color"], width * 2 / 3))
        label = kit.math([f"{value:g}"], spec.get("label_size", "tick"), spec["label_color"])
        parts.append(kit.place(label, x, y + tick / 2 + kit.size_px(spec.get("label_size", "tick"))))
    return m.VGroup(*parts)


def axes(spec: dict, kit: Kit) -> m.Mobject:
    """Plain x/y axes with arrow tips, 3b1b grey, no grid.

    Fields:
        x0, y0, x1, y1: The plot rectangle (px); the axes run along its left and bottom edges.
        color: Axis colour (palette token), default ``grey_light``.
        stroke_width: Axis width (px), default 3.

    Args:
        spec: The layout entry.
        kit: Unit conversion and builders.

    Returns:
        A VGroup of the two axis arrows.
    """
    color = spec.get("color", "grey_light")
    width = spec.get("stroke_width", 3)
    x0, y0, x1, y1 = spec["x0"], spec["y0"], spec["x1"], spec["y1"]
    return m.VGroup(kit.arrow([x0, y1], [x1, y1], color, width, 4 * width),
                    kit.arrow([x0, y1], [x0, y0], color, width, 4 * width))


def curve(spec: dict, kit: Kit) -> m.Mobject:
    """A smooth curve through canvas points (a plotted function, sampled by the planner).

    Fields:
        points: ``[[x, y], ...]`` in px, at least three.
        stroke: Colour token.
        stroke_width: Width (px), default 4.

    Args:
        spec: The layout entry.
        kit: Unit conversion and builders.

    Returns:
        The curve.
    """
    curve_mob = m.VMobject(color=kit.color(spec["stroke"]), stroke_width=kit.stroke(spec.get("stroke_width", 4)))
    return curve_mob.set_points_smoothly([kit.pt(*p) for p in spec["points"]])
