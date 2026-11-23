"""Build layout objects as manimgx mobjects, in the style's fonts and colours.

Coordinates in the layout are canvas pixels (origin top-left, y down). manimgx works in
scene units with the frame 8 units tall, so one unit is ``canvas.height / 8`` px (135 px at
1080p). Text sizes are CSS font sizes (the em) in px; stroke widths are px.

The ``Kit`` is the one place that converts units and builds primitives; layout objects,
style components and video-specific components all go through it.
"""

from functools import cache
from pathlib import Path
from types import ModuleType

import manimgx as m
import numpy as np

from explain.plan import Layout
from explain.styles import Style, import_file

FRAME_HEIGHT_UNITS = 8.0
ANCHOR_EDGES = {"center": m.ORIGIN, "left": m.LEFT, "right": m.RIGHT}
BRACE_SIDES = {"down": m.DOWN, "up": m.UP, "left": m.LEFT, "right": m.RIGHT}


class Kit:
    """Unit conversion and primitive builders in one style.

    Args:
        style: The series' style pack.
    """

    def __init__(self, style: Style) -> None:
        """Keep the style and work out how many pixels one scene unit is.

        Args:
            style: The series' style pack (its canvas sets the scale).
        """
        self.style = style
        self.px_per_unit = style.canvas.height / FRAME_HEIGHT_UNITS

    def pt(self, x: float, y: float) -> np.ndarray:
        """Convert a canvas point to a scene point.

        Args:
            x: Pixels from the left edge.
            y: Pixels from the top edge (downward).

        Returns:
            The scene point (z = 0).
        """
        w, h = self.style.canvas.width, self.style.canvas.height
        return np.array([(x - w / 2) / self.px_per_unit, (h / 2 - y) / self.px_per_unit, 0.0])

    def to_px(self, point: np.ndarray) -> tuple[float, float]:
        """Convert a scene point back to canvas pixels.

        Args:
            point: A scene point.

        Returns:
            ``(x, y)`` in canvas pixels.
        """
        w, h = self.style.canvas.width, self.style.canvas.height
        return float(point[0] * self.px_per_unit + w / 2), float(h / 2 - point[1] * self.px_per_unit)

    def units(self, px: float) -> float:
        """Convert a length in pixels to scene units.

        Args:
            px: The length in pixels.

        Returns:
            The length in scene units.
        """
        return px / self.px_per_unit

    def stroke(self, px: float) -> float:
        """Convert a stroke width in pixels to manimgx's stroke unit (hundredths of a unit).

        Args:
            px: The width in pixels.

        Returns:
            The manimgx stroke width.
        """
        return px / (0.01 * self.px_per_unit)

    def color(self, token: str | None) -> str | None:
        """Resolve a palette token (None passes through).

        Args:
            token: A palette key or None.

        Returns:
            The hex colour, or None.
        """
        return None if token is None else self.style.color(token)

    def size_px(self, size: float | str) -> float:
        """Resolve a text size: a number of px, or a role name from the style.

        Args:
            size: Pixels, or a key of ``style.text.roles``.

        Returns:
            The size in px.
        """
        return float(self.style.text.roles[size]) if isinstance(size, str) else float(size)

    def text(self, content: str, size: float | str, color: str, backstroke: bool = False,
             family: str = "default", weight: str = "NORMAL", slant: str = "NORMAL") -> m.Mobject:
        """Build text in one of the style's fonts, its em ``size`` px tall.

        Args:
            content: The text.
            size: Pixels or a size role.
            color: Palette token.
            backstroke: Draw the style's black stroke behind the glyphs.
            family: A font name from the style's ``families`` (``default`` unless set).
            weight: ``NORMAL``, ``SEMIBOLD`` or ``BOLD``.
            slant: ``NORMAL`` or ``ITALIC``.

        Returns:
            The (unplaced) Text.
        """
        name, font_dir = self.style.text.families[family]
        mob = m.Text(content, font=name, font_paths=[str(font_dir)], weight=weight, slant=slant,
                     font_size=text_font_size(name, str(font_dir), self.units(self.size_px(size))),
                     color=self.color(color))
        return self.backstroke(mob) if backstroke else mob

    def math(self, pieces: list[str], size: float | str, color: str, backstroke: bool = False) -> m.MathTex:
        """Build LaTeX math (manimgx converts it to Typst), its em ``size`` px tall.

        Args:
            pieces: LaTeX pieces; each becomes one submobject (``mob[i]``).
            size: Pixels or a size role.
            color: Palette token for every piece.
            backstroke: Draw the style's black stroke behind the glyphs.

        Returns:
            The (unplaced) MathTex.
        """
        mob = m.MathTex(*pieces, font_size=self.units(self.size_px(size)) * 96, color=self.color(color))
        return self.backstroke(mob) if backstroke else mob

    def backstroke(self, mob: m.Mobject) -> m.Mobject:
        """Give glyphs the style's black background stroke (3b1b ``set_backstroke``).

        Args:
            mob: Text or math.

        Returns:
            The same mobject.
        """
        mob.set_stroke(m.BLACK, width=self.stroke(self.style.text.backstroke_px), opacity=1.0, background=True)
        return mob

    def place(self, mob: m.Mobject, x: float, y: float, anchor: str = "center") -> m.Mobject:
        """Move a mobject so its anchor point sits at a canvas point.

        Args:
            mob: The mobject.
            x: Canvas x of the anchor: the centre, or the left/right edge.
            y: Canvas y of the vertical centre.
            anchor: ``center``, ``left`` or ``right``.

        Returns:
            The same mobject.
        """
        mob.move_to(self.pt(x, y), aligned_edge=ANCHOR_EDGES[anchor])
        return mob

    def rect(self, x0: float, y0: float, x1: float, y1: float, fill: str | None = None,
             fill_opacity: float = 1.0, stroke: str | None = None, stroke_width: float = 0.0,
             corner_radius: float = 0.0) -> m.Mobject:
        """Build a rectangle from its canvas corners.

        Args:
            x0: Left edge (px).
            y0: Top edge (px).
            x1: Right edge (px).
            y1: Bottom edge (px).
            fill: Fill palette token, or None for no fill.
            fill_opacity: Fill opacity.
            stroke: Stroke palette token, or None for no stroke.
            stroke_width: Stroke width (px).
            corner_radius: Corner radius (px); 0 for square corners.

        Returns:
            The placed rectangle.
        """
        size = {"width": self.units(x1 - x0), "height": self.units(y1 - y0)}
        look = {"fill_color": self.color(fill) or m.BLACK, "fill_opacity": fill_opacity if fill else 0.0,
                "stroke_color": self.color(stroke) or self.color(fill) or m.BLACK,
                "stroke_width": self.stroke(stroke_width) if stroke else 0.0}
        mob = (m.RoundedRectangle(corner_radius=self.units(corner_radius), **size, **look)
               if corner_radius else m.Rectangle(**size, **look))
        return mob.move_to(self.pt((x0 + x1) / 2, (y0 + y1) / 2))

    def polyline(self, points: list[list[float]], stroke: str, stroke_width: float,
                 dash: list[float] | None = None, opacity: float = 1.0) -> m.Mobject:
        """Build a line through canvas points, solid or dashed.

        Args:
            points: Two or more ``[x, y]`` points.
            stroke: Palette token.
            stroke_width: Width (px).
            dash: ``[on, off]`` dash lengths (px) for a dashed two-point line.
            opacity: Stroke opacity.

        Returns:
            The line.
        """
        look = {"color": self.color(stroke), "stroke_width": self.stroke(stroke_width), "stroke_opacity": opacity}
        ends = [self.pt(*p) for p in points]
        if dash:
            on, off = dash
            return m.DashedLine(ends[0], ends[-1], dash_length=self.units(on), dashed_ratio=on / (on + off), **look)
        if len(ends) == 2:
            return m.Line(ends[0], ends[1], **look)
        return m.VMobject(**look).set_points_as_corners(ends)

    def symbol(self, glyph: str, x: float, y: float, size: float, color: str,
               stroke_width: float | None = None) -> m.Mobject:
        """Draw +, −, × or = as strokes: font glyphs this small are hairlines.

        Args:
            glyph: One of ``+``, ``−``, ``×``, ``=``.
            x: Centre x (px).
            y: Centre y (px).
            size: Width of the symbol (px).
            color: Palette token.
            stroke_width: Stroke width (px); defaults to a seventh of the size, at least 4.

        Returns:
            A VGroup of the strokes.
        """
        h = size / 2
        width = stroke_width if stroke_width is not None else max(4.0, size / 7)
        strokes = {
            "+": [[[x - h, y], [x + h, y]], [[x, y - h], [x, y + h]]],
            "−": [[[x - h, y], [x + h, y]]],
            "×": [[[x - h * 0.8, y - h * 0.8], [x + h * 0.8, y + h * 0.8]],
                  [[x - h * 0.8, y + h * 0.8], [x + h * 0.8, y - h * 0.8]]],
            "=": [[[x - h, y - h * 0.4], [x + h, y - h * 0.4]], [[x - h, y + h * 0.4], [x + h, y + h * 0.4]]],
        }[glyph]
        return m.VGroup(*(self.polyline(points, color, width) for points in strokes))

    def arrow(self, tail: list[float], head: list[float], stroke: str, stroke_width: float,
              tip_length: float | None = None, fraction: float = 1.0) -> m.Arrow:
        """Build an arrow from a tail toward a head, drawn to a fraction of the full length.

        Args:
            tail: ``[x, y]`` of the tail (px).
            head: ``[x, y]`` of the full-length head (px).
            stroke: Palette token.
            stroke_width: Shaft width (px).
            tip_length: Tip length (px); defaults to three shaft widths.
            fraction: Share of the full length to draw, from the tail.

        Returns:
            The arrow.
        """
        a, b = self.pt(*tail), self.pt(*head)
        return m.Arrow(a, a + fraction * (b - a), buff=0, color=self.color(stroke),
                       stroke_width=self.stroke(stroke_width),
                       tip_length=self.units(tip_length if tip_length is not None else 3 * stroke_width),
                       max_tip_length_to_length_ratio=1.0, max_stroke_width_to_length_ratio=1000)


@cache
def text_font_size(family: str, font_dir: str, em_units: float) -> float:
    """The manimgx ``Text`` font_size whose em is ``em_units`` scene units in this family.

    ``Text`` normalises every font so a capital is the same height at a given size; layout
    sizes are ems. This measures the family's cap height per em with a raw Typst probe (an
    em is font_size / 96 units there) and undoes the normalisation.

    Args:
        family: Font family.
        font_dir: Directory with the family's files.
        em_units: The wanted em in scene units.

    Returns:
        The font_size to pass to ``Text``.
    """
    cap_per_em = m.Typst(f'#text(font: "{family}")[H]', font_size=96, font_paths=[font_dir]).height
    cap_at_48 = m.Text("H", font=family, font_paths=[font_dir], font_size=48).height
    return 48 * cap_per_em * em_units / cap_at_48


class Builder:
    """Builds the mobject of every layout object, and rebuilds them for ``change``.

    Args:
        style: The series' style pack.
        layout: The video's layout plan.
        custom: Path to the video's ``custom.py`` (components named ``custom:<name>``).
    """

    def __init__(self, style: Style, layout: Layout, custom: Path) -> None:
        """Prepare the kit and load the style's and the video's component modules.

        Args:
            style: The series' style pack.
            layout: The video's layout plan.
            custom: Path to the video's ``custom.py``; it may not exist.
        """
        self.kit = Kit(style)
        self.layout = layout
        self.style_components = style.components()
        self.custom_components: ModuleType | None = (
            import_file(custom, "explain_custom_components") if custom.is_file() else None)

    def build_all(self) -> dict[str, m.Mobject]:
        """Build every object, registering math parts under their own ids.

        ``box`` and ``brace`` objects are built last, around their (already built) targets.

        Returns:
            Leaf or object id → mobject, each with its layout ``z`` as z-index.
        """
        reg: dict[str, m.Mobject] = {}
        deferred = []
        for oid, spec in self.layout.objects.items():
            if spec["type"] in ("box", "brace"):
                deferred.append((oid, spec))
                continue
            reg[oid] = self.build(spec, reg)
            for i, part in enumerate(spec.get("parts") or []):
                if part.get("id"):
                    reg[part["id"]] = reg[oid][i]
        for oid, spec in deferred:
            reg[oid] = self.build(spec, reg)
        return reg

    def build(self, spec: dict, reg: dict[str, m.Mobject]) -> m.Mobject:
        """Build one object from its spec.

        Args:
            spec: The object's layout entry (possibly with ``change`` overrides applied).
            reg: Mobjects built so far (``box``/``brace`` look up their target there).

        Returns:
            The placed mobject, with z-index set.

        Raises:
            ValueError: For a component name that neither the style nor the video defines.
        """
        k = self.kit
        kind = spec["type"]
        if kind == "text":
            mob = k.text(spec["content"], spec["size"], spec["color"], spec.get("backstroke", False),
                         spec.get("family", "default"), spec.get("weight", "NORMAL"), spec.get("slant", "NORMAL"))
            k.place(mob, spec["x"], spec["y"], spec.get("anchor", "center"))
        elif kind == "math":
            parts = spec.get("parts") or [{"tex": spec["tex"]}]
            mob = k.math([p["tex"] for p in parts], spec["size"], spec["color"], spec.get("backstroke", False))
            for i, part in enumerate(parts):
                if part.get("color"):
                    mob[i].set_color(k.color(part["color"]))
            k.place(mob, spec["x"], spec["y"], spec.get("anchor", "center"))
        elif kind == "circle":
            mob = m.Circle(radius=k.units(spec["r"]), fill_color=k.color(spec["fill"]),
                           fill_opacity=spec.get("fill_opacity", 1.0),
                           stroke_color=k.color(spec.get("stroke")) or k.color(spec["fill"]),
                           stroke_width=k.stroke(spec.get("stroke_width", 0)) if spec.get("stroke") else 0)
            mob.move_to(k.pt(spec["cx"], spec["cy"]))
        elif kind == "rect":
            mob = k.rect(spec["x0"], spec["y0"], spec["x1"], spec["y1"], spec.get("fill"),
                         spec.get("fill_opacity", 1.0), spec.get("stroke"), spec.get("stroke_width", 0),
                         spec.get("corner_radius", 0))
        elif kind == "line":
            mob = k.polyline(spec["points"], spec["stroke"], spec["stroke_width"], spec.get("dash"),
                             spec.get("stroke_opacity", 1.0))
        elif kind == "arrow":
            tail, head = spec["points"]
            mob = k.arrow(tail, head, spec["stroke"], spec["stroke_width"], spec.get("tip_length"),
                          spec.get("fraction", 1.0))
        elif kind == "polygon":
            mob = m.Polygon(*(k.pt(*p) for p in spec["points"]), fill_color=k.color(spec["fill"]),
                            fill_opacity=spec.get("fill_opacity", 1.0),
                            stroke_color=k.color(spec.get("stroke")) or k.color(spec["fill"]),
                            stroke_width=k.stroke(spec.get("stroke_width", 0)) if spec.get("stroke") else 0)
        elif kind == "symbol":
            mob = k.symbol(spec["glyph"], spec["x"], spec["y"], spec["size"], spec["color"], spec.get("stroke_width"))
        elif kind == "box":
            target = reg[spec["around"]]
            pad = k.units(spec["padding"])
            mob = m.RoundedRectangle(width=target.width + 2 * pad, height=target.height + 2 * pad,
                                     corner_radius=k.units(spec.get("corner_radius", 0)),
                                     color=k.color(spec["stroke"]), stroke_width=k.stroke(spec["stroke_width"]),
                                     fill_opacity=0).move_to(target.get_center())
        elif kind == "brace":
            mob = m.Brace(reg[spec["around"]], direction=BRACE_SIDES[spec["side"]], color=k.color(spec["color"]))
        else:
            mob = self.component(spec)
        mob.set_z_index(spec.get("z", 0))
        return mob

    def component(self, spec: dict) -> m.Mobject:
        """Build a ``component`` object: a style component, or ``custom:<name>`` from custom.py.

        A component is a function ``(spec, kit) -> Mobject`` that places itself.

        Args:
            spec: The layout entry (``name`` plus the component's own fields).

        Returns:
            The component's mobject.

        Raises:
            ValueError: If no such component exists.
        """
        name = spec["name"]
        module = self.style_components
        if name.startswith("custom:"):
            module, name = self.custom_components, name.removeprefix("custom:")
        func = getattr(module, name, None) if module is not None else None
        if func is None or name.startswith("_"):
            raise ValueError(f"Unknown component {spec['name']!r}")
        return func(spec, self.kit)
