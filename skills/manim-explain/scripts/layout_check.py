"""AABB overlap checks for Manim text / math layout.

Use at authoring time (LayoutBoard.assert_clear) and in pytest snapshots.
Pure geometry helpers work without Manim; mobject helpers need Manim CE.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


# Classic Manim frame ≈ 14.22 × 8; keep a thin margin inside the camera
SAFE_X = (-6.8, 6.8)
SAFE_Y = (-3.8, 3.85)

# Reserved horizontal bands (manim units) — must not overlap each other
# Keep clear gutters between bands; KEY must be tall enough for readable prose.
TITLE_BAND = (3.05, 3.95)  # section titles
KEY_BAND = (2.25, 2.95)  # parked / banner key sentences (title must be gone)
PANEL_LABEL_BAND = (1.70, 2.10)  # "spread" / "piled" style names
BOTTOM_BAND = (-3.55, -2.75)


@dataclass(frozen=True)
class Box:
    """Axis-aligned bounding box in manim plane coordinates."""

    x_min: float
    y_min: float
    x_max: float
    y_max: float
    label: str = ""

    @property
    def width(self) -> float:
        return self.x_max - self.x_min

    @property
    def height(self) -> float:
        return self.y_max - self.y_min

    def padded(self, pad: float) -> "Box":
        return Box(
            self.x_min - pad,
            self.y_min - pad,
            self.x_max + pad,
            self.y_max + pad,
            self.label,
        )

    def overlaps(self, other: "Box", pad: float = 0.0) -> bool:
        a = self.padded(pad) if pad else self
        b = other.padded(pad) if pad else other
        if a.x_max <= b.x_min or b.x_max <= a.x_min:
            return False
        if a.y_max <= b.y_min or b.y_max <= a.y_min:
            return False
        return True

    def outside_safe(
        self,
        x_range: tuple[float, float] = SAFE_X,
        y_range: tuple[float, float] = SAFE_Y,
    ) -> bool:
        return (
            self.x_min < x_range[0]
            or self.x_max > x_range[1]
            or self.y_min < y_range[0]
            or self.y_max > y_range[1]
        )


def boxes_overlap(a: Box, b: Box, pad: float = 0.05) -> bool:
    return a.overlaps(b, pad=pad)


def find_overlaps(boxes: Sequence[Box], pad: float = 0.05) -> list[tuple[Box, Box]]:
    hits: list[tuple[Box, Box]] = []
    for i, a in enumerate(boxes):
        for b in boxes[i + 1 :]:
            if boxes_overlap(a, b, pad=pad):
                hits.append((a, b))
    return hits


def find_out_of_bounds(boxes: Sequence[Box]) -> list[Box]:
    return [b for b in boxes if b.outside_safe()]


def format_overlap_report(hits: Sequence[tuple[Box, Box]]) -> str:
    lines = []
    for a, b in hits:
        lines.append(
            f"  overlap: '{a.label}' {(_fmt(a))} ↔ '{b.label}' {(_fmt(b))}"
        )
    return "\n".join(lines)


def _fmt(b: Box) -> str:
    return f"[{b.x_min:.2f},{b.y_min:.2f}]–[{b.x_max:.2f},{b.y_max:.2f}]"


def assert_no_overlaps(boxes: Sequence[Box], pad: float = 0.05) -> None:
    hits = find_overlaps(boxes, pad=pad)
    if hits:
        raise AssertionError(
            f"{len(hits)} layout overlap(s):\n{format_overlap_report(hits)}"
        )


def assert_in_safe_frame(boxes: Sequence[Box]) -> None:
    bad = find_out_of_bounds(boxes)
    if bad:
        detail = "\n".join(f"  oob: '{b.label}' {_fmt(b)}" for b in bad)
        raise AssertionError(f"{len(bad)} mobject(s) outside safe frame:\n{detail}")


def mobject_box(mob, label: str | None = None) -> Box:
    """Build a Box from a Manim Mobject (needs manim imported by caller)."""
    left = float(mob.get_left()[0])
    right = float(mob.get_right()[0])
    bottom = float(mob.get_bottom()[1])
    top = float(mob.get_top()[1])
    name = label if label is not None else type(mob).__name__
    return Box(left, bottom, right, top, name)

def collect_boxes(
    items: Iterable[tuple[object, str]] | Iterable[object],
) -> list[Box]:
    boxes: list[Box] = []
    for item in items:
        if isinstance(item, tuple) and len(item) == 2:
            mob, label = item
            boxes.append(mobject_box(mob, label))
        else:
            boxes.append(mobject_box(item))
    return boxes


def place_in_band(mob, y_center: float, *, x: float = 0.0, max_width: float | None = None):
    """Move mobject so its center sits on (x, y_center); optionally fit width."""
    if max_width is not None and mob.width > max_width:
        mob.scale_to_fit_width(max_width)
    mob.move_to([x, y_center, 0])
    return mob


def park_key_sentence(mob, *, side: str = "left", y: float | None = None):
    """Park a key line in the KEY_BAND (never the TITLE_BAND)."""
    y_c = y if y is not None else sum(KEY_BAND) / 2
    if mob.width > 7.5:
        mob.scale_to_fit_width(7.5)
    half_h = mob.height / 2
    # Clamp so the whole box stays inside KEY_BAND
    y_lo, y_hi = KEY_BAND
    y_c = min(max(y_c, y_lo + half_h), y_hi - half_h)
    if side == "right":
        x = SAFE_X[1] - 0.35 - mob.width / 2
        mob.move_to([x, y_c, 0])
    else:
        x = SAFE_X[0] + 0.35 + mob.width / 2
        mob.move_to([x, y_c, 0])
    return mob