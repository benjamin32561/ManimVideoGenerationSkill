"""Shared style for classic 3b1b-look explainers.

Includes LayoutBoard — reserved bands + overlap asserts so titles,
parked key lines, panel labels, and bottom notes do not collide.
"""

# ruff: noqa: F403, F405
from __future__ import annotations

import atexit
import os
import sys
import traceback
from pathlib import Path

from manim import *

# layout_check lives with skill scripts — resolve from repo or this file
def _find_scripts() -> Path:
    """Locate the skill's ``scripts/`` directory from anywhere.

    This module is copied into each demo, so it must find the skill whether the
    skill lives in the project (``skills/manim-explain``), in a tool directory
    (``.claude/skills``, ``.cursor/skills``, ``.agents/skills``), or under
    ``$HOME``. ``MANIM_EXPLAIN_ROOT`` (exported by ``scripts/env.sh``) wins.

    Returns:
        Absolute path to the directory containing ``layout_check.py``.

    Raises:
        FileNotFoundError: If no installed copy of the skill can be found.
    """
    env_root = os.environ.get("MANIM_EXPLAIN_ROOT")
    if env_root and (Path(env_root) / "scripts" / "layout_check.py").is_file():
        return Path(env_root) / "scripts"

    here = Path(__file__).resolve()
    # style.py used in place inside the skill (assets/style.py)
    sibling = here.parent.parent / "scripts"
    if (sibling / "layout_check.py").is_file():
        return sibling

    skill_dirs = ("skills", ".claude/skills", ".cursor/skills", ".agents/skills")
    for base in [*here.parents, Path.home()]:
        for rel in skill_dirs:
            candidate = base / rel / "manim-explain" / "scripts"
            if (candidate / "layout_check.py").is_file():
                return candidate
    raise FileNotFoundError(
        "Cannot locate the manim-explain skill scripts. Set MANIM_EXPLAIN_ROOT "
        "to the directory containing SKILL.md, or source scripts/env.sh first."
    )


_SCRIPTS = _find_scripts()
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from layout_check import (  # noqa: E402
    BOTTOM_BAND,
    KEY_BAND,
    PANEL_LABEL_BAND,
    TITLE_BAND,
    assert_in_safe_frame,
    assert_no_overlaps,
    collect_boxes,
    find_out_of_bounds,
    find_overlaps,
    format_overlap_report,
    mobject_box,
    park_key_sentence,
)

# Semantic palette (classic 3b1b-ish)
C = {
    "primary": BLUE_C,
    "secondary": TEAL_C,
    "accent": YELLOW_C,
    "highlight": PURE_YELLOW,
    "wrong": RED_C,
    "right": GREEN_C,
    "dim": GREY_B,
    "label": GREY_A,
    "gold": GOLD_C,
}

TITLE_SIZE = 48
SUBTITLE_SIZE = 32
BODY_SIZE = 28
LABEL_SIZE = 22
EQ_SIZE = 40

TITLE_Y = sum(TITLE_BAND) / 2
BOTTOM_Y = sum(BOTTOM_BAND) / 2
SAFE_WIDTH = 12.0
PANEL_LABEL_Y = sum(PANEL_LABEL_BAND) / 2
BAR_FLOOR_Y = -1.85
BAR_MAX_HEIGHT = 2.0  # tallest bar top stays under panel-label band with gutter


def safe_text(text: str, font_size: int = BODY_SIZE, color=WHITE, max_width: float = SAFE_WIDTH) -> Text:
    t = Text(text, font_size=font_size, color=color)
    if t.width > max_width:
        t.scale_to_fit_width(max_width)
    return t


def safe_multiline(
    *lines: str,
    font_size: int = BODY_SIZE,
    color=WHITE,
    line_buff: float = 0.28,
    max_width: float = SAFE_WIDTH,
) -> VGroup:
    texts = []
    for line in lines:
        t = Text(line, font_size=font_size, color=color)
        if t.width > max_width:
            t.scale_to_fit_width(max_width)
        texts.append(t)
    return VGroup(*texts).arrange(DOWN, buff=line_buff, center=True)


def section_title(text: str, color=WHITE) -> Text:
    t = safe_text(text, font_size=36, color=color, max_width=11.0)
    t.move_to(UP * TITLE_Y)
    return t


def bottom_note(text: str, color=YELLOW_C) -> Text:
    t = safe_text(text, font_size=LABEL_SIZE, color=color, max_width=11.5)
    t.move_to([0.0, BOTTOM_Y, 0.0])
    return t


def panel_label(text: str, color=WHITE, x: float = 0.0) -> Text:
    """Panel name parked in the reserved band above charts."""
    t = Text(text, font_size=24, color=color)
    t.move_to(RIGHT * x + UP * PANEL_LABEL_Y)
    return t


def ask_about(
    scene: Scene,
    text: str,
    *referents,
    color=YELLOW_C,
    font_size: int = 28,
    hold: float = 0.35,
    park: str | None = "left",
    board: LayoutBoard | None = None,
    motion_time: float = 1.1,
    placement: str = "key",
) -> Text:
    """Show a question while its referent objects move (craft law).

    If VO asks how/which/what about X, pass the mobjects that *are* X as referents
    so the viewer sees what is changing while the question is asked.

    ``placement``:
      - ``\"key\"`` (default): appear in KEY_BAND above the stage — never over a live graph
      - ``\"bottom\"``: BOTTOM_BAND
      - ``\"center\"``: frame center — **only** when the stage figure is cleared first
    """
    if color == YELLOW_C:
        color = C.get("highlight", PURE_YELLOW)
    t = safe_text(text, font_size=font_size, color=color, max_width=11.5)
    if placement == "bottom":
        t.move_to([0.0, BOTTOM_Y, 0.0])
    elif placement == "center":
        t.move_to(ORIGIN)
    else:
        if t.width > 11.5:
            t.scale_to_fit_width(11.5)
        max_h = (KEY_BAND[1] - KEY_BAND[0]) * 0.95
        if t.height > max_h:
            t.scale_to_fit_height(max_h)
        t.set_color(color)
        t.set_opacity(1.0)
        t.move_to([0.0, sum(KEY_BAND) / 2, 0.0])

    motion = [Indicate(m, color=color, scale_factor=1.06) for m in referents]
    if motion:
        scene.play(FadeIn(t, shift=DOWN * 0.08), *motion, run_time=motion_time, rate_func=smooth)
    else:
        scene.play(FadeIn(t, shift=DOWN * 0.08), run_time=0.55, rate_func=smooth)
    if hold > 0:
        scene.wait(hold)
    if park and placement != "center":
        parked = t.copy()
        park_key_sentence(parked, side=park)
        scene.play(Transform(t, parked), run_time=0.65, rate_func=smooth)
        if board is not None:
            board.slots.pop("title", None)
            board.set_key(t, side=park)
            board.assert_clear()
    elif park and placement == "center":
        parked = t.copy().scale(0.68)
        park_key_sentence(parked, side=park)
        scene.play(Transform(t, parked), run_time=0.75, rate_func=smooth)
        if board is not None:
            board.slots.pop("title", None)
            board.set_key(t, side=park)
            board.assert_clear()
    elif board is not None and placement == "key":
        board.slots.pop("title", None)
        board.slots["key"] = t
        board.assert_clear()
    elif board is not None and placement == "bottom":
        board.slots["bottom"] = t
        board.assert_clear()
    return t


def soft_idle(scene: Scene, *mobs, run_time: float = 0.9, scale: float = 1.02) -> None:
    """Gentle breathe on holds — craft law: soft idle, not freeze."""
    if not mobs:
        return
    scene.play(
        *[m.animate.scale(scale) for m in mobs],
        run_time=run_time,
        rate_func=there_and_back,
    )


def breathe_until(scene: Scene, clock, bookmark: str, *mobs, cadence: float = 1.1,
                  gap: float = 0.45, scale: float = 1.015) -> None:
    """Keep a figure alive until a cue, instead of freezing after one breath.

    A single ``soft_idle`` covers about a second; a cue eight seconds away leaves
    seven seconds of frozen frame while the narration keeps talking. This repeats
    gentle idles until the cue is nearly due, so the picture never stops moving
    mid-sentence.

    Args:
        scene: The running scene.
        clock: Anything exposing ``span_until(bookmark)`` — normally the
            ``TimedNarration``.
        bookmark: Cue to breathe up to.
        mobs: Mobjects to idle; no-op when empty.
        cadence: Length of each individual breath.
        gap: Silence deliberately left before the cue lands.
        scale: Breath amplitude — keep it subtle.
    """
    if not mobs:
        return
    while True:
        remaining = float(clock.span_until(bookmark))
        if remaining <= gap + 0.2:
            return
        run = min(cadence, remaining - gap)
        if run < 0.25:
            return
        soft_idle(scene, *mobs, run_time=run, scale=scale)


def pop_named(
    scene: Scene,
    *mobs,
    color=YELLOW_C,
    run_time: float = 0.7,
    settle: float = 0.3,
    scale_factor: float = 1.18,
) -> None:
    """Emphasize a just-named object, then short settle (craft law)."""
    if not mobs:
        return
    scene.play(
        *[Indicate(m, color=color, scale_factor=scale_factor) for m in mobs],
        run_time=run_time,
        rate_func=there_and_back,
    )
    if settle > 0:
        soft_idle(scene, *mobs, run_time=settle)


def _on_stage_ids() -> set | None:
    """Ids of everything currently drawn, when a watcher has attached a scene.

    Returns:
        A set of ``id()`` values, or ``None`` when no scene is available (in
        which case the caller must not filter anything out).
    """
    try:
        from layout_watch import active_scene, on_stage_ids
    except Exception:  # noqa: BLE001 - the board works without the watcher
        return None
    scene = active_scene()
    if scene is None:
        return None
    try:
        return on_stage_ids(scene)
    except Exception:  # noqa: BLE001
        return None


def _visible_opacity(mob: object) -> float:
    """Best-effort visible opacity of a tracked mobject.

    Args:
        mob: Any Manim mobject held in a board slot.

    Returns:
        The larger of fill and stroke opacity, or 1.0 when it cannot be read
        (an unreadable mobject is assumed visible, so nothing is skipped by
        accident).
    """
    try:
        fill = float(mob.get_fill_opacity())
    except Exception:  # noqa: BLE001 - not all mobjects carry a fill
        fill = 0.0
    try:
        stroke = float(mob.get_stroke_opacity())
    except Exception:  # noqa: BLE001 - nor a stroke
        stroke = 0.0
    if fill == 0.0 and stroke == 0.0:
        try:                                # a group: take the brightest child
            kids = mob.family_members_with_points()
        except Exception:  # noqa: BLE001
            return 1.0
        if not kids:
            return 1.0
        return max((_visible_opacity(k) for k in kids if k is not mob), default=1.0)
    return max(fill, stroke)


_COLLECT_LAYOUT = os.environ.get("MANIM_LAYOUT_COLLECT", "") not in ("", "0")
_LAYOUT_FAILURES: dict[str, str] = {}


def _layout_call_site() -> str:
    """Describe the scene line that called ``assert_clear``.

    Returns:
        ``"file.py:123"`` for the nearest frame outside this module, or
        ``"?"`` when the stack cannot be read.
    """
    here = os.path.basename(__file__)
    for frame in reversed(traceback.extract_stack()[:-2]):
        name = os.path.basename(frame.filename)
        if name != here:
            return f"{name}:{frame.lineno}"
    return "?"


def _collect_layout_failure(boxes, pad: float) -> None:
    """Record, rather than raise, the failures at one ``assert_clear`` site.

    Args:
        boxes: The tracked boxes at this call.
        pad: Clearance padding applied to both boxes of a pair.
    """
    parts = []
    hits = find_overlaps(boxes, pad=pad)
    if hits:
        parts.append(format_overlap_report(hits))
    bad = find_out_of_bounds(boxes)
    if bad:
        parts.extend(f"  oob: '{b.label}' [{b.x_min:.2f},{b.y_min:.2f}]"
                     f"-[{b.x_max:.2f},{b.y_max:.2f}]" for b in bad)
    if parts:
        _LAYOUT_FAILURES.setdefault(_layout_call_site(), "\n".join(parts))


def _report_collected_layout() -> None:
    """Print every recorded layout failure, grouped by call site."""
    if not _LAYOUT_FAILURES:
        if _COLLECT_LAYOUT:
            print("\nLAYOUT SURVEY: no assert_clear site reported a problem.")
        return
    print(f"\nLAYOUT SURVEY: {len(_LAYOUT_FAILURES)} assert_clear site(s) would fail:")
    for site, detail in _LAYOUT_FAILURES.items():
        print(f"  at {site}")
        for line in detail.splitlines():
            print(f"  {line}")


if _COLLECT_LAYOUT:
    atexit.register(_report_collected_layout)


class LayoutBoard:
    """Track on-screen text/math and fail fast on overlaps.

    Slots are mutually exclusive for their band:
      title | key | bottom
    Extra labels/equations go into ``extras`` and are checked pairwise.
    """

    def __init__(self, *, pad: float = 0.08, enforce: bool | None = None):
        self.pad = pad
        if enforce is None:
            enforce = os.environ.get("MANIM_LAYOUT_ASSERT", "1") != "0"
        self.enforce = enforce
        self.slots: dict[str, object] = {}
        self.extras: list[tuple[object, str]] = []

    def clear(self, *names: str) -> None:
        if not names:
            self.slots.clear()
            self.extras.clear()
            return
        for n in names:
            self.slots.pop(n, None)
        self.extras = [(m, lab) for m, lab in self.extras if lab not in names]

    def set_title(self, mob) -> object:
        mob.move_to(UP * TITLE_Y)
        self.slots["title"] = mob
        return mob

    def set_bottom(self, mob) -> object:
        if mob.width > 11.5:
            mob.scale_to_fit_width(11.5)
        mob.set_y(BOTTOM_Y)
        self.slots["bottom"] = mob
        return mob

    def set_key(self, mob, *, side: str = "left") -> object:
        park_key_sentence(mob, side=side)
        self.slots["key"] = mob
        return mob

    def add(self, mob, label: str) -> object:
        self.extras.append((mob, label))
        return mob

    def tracked_items(self) -> list[tuple[object, str]]:
        items: list[tuple[object, str]] = []
        for name, mob in self.slots.items():
            items.append((mob, name))
        items.extend(self.extras)
        return items

    def assert_clear(self) -> None:
        """Check every tracked figure for overlap and frame violations.

        Raises:
            AssertionError: On the first overlap or out-of-frame figure, so the
                render stops where the problem is.

        Notes:
            With ``MANIM_LAYOUT_COLLECT=1`` in the environment, failures are
            recorded with their call site and printed at exit instead of
            raising. One logic pass then reports *every* bad placement in the
            scene rather than only the earliest, which turns a chain of
            one-fix-per-render cycles into a single round. Set it only for that
            survey — a collecting render is not a passing render.
        """
        if not self.enforce:
            return
        # A disposed figure keeps its coordinates, so a slot that was never
        # cleared contributes a phantom box that collides with everything later
        # placed there — a whole class of false failures that used to be chased
        # as real ones. Manim's FadeOut *restores* opacity and merely removes the
        # mobject from the scene, so membership is the reliable test and opacity
        # is the fallback for figures faded in place.
        items = list(self.tracked_items())
        stage = _on_stage_ids()
        if stage is not None:
            items = [(m, n) for m, n in items if id(m) in stage]
        items = [(m, n) for m, n in items if _visible_opacity(m) > 0.02]
        boxes = collect_boxes(items)
        # Drop degenerate / tiny boxes (empty groups)
        boxes = [b for b in boxes if b.width > 0.01 and b.height > 0.01]
        if _COLLECT_LAYOUT:
            _collect_layout_failure(boxes, self.pad)
            return
        assert_no_overlaps(boxes, pad=self.pad)
        assert_in_safe_frame(boxes)


def key_sentence(
    scene: Scene,
    text: str,
    *,
    color=YELLOW_C,
    font_size: int = 30,
    hold: float = 0.6,
    park: str | None = "left",
    board: LayoutBoard | None = None,
    placement: str = "key",
) -> Text:
    """Key line in a reserved band — never over a live mid-stage figure.

    Default ``placement=\"key\"`` puts the line in KEY_BAND immediately.
    Use ``placement=\"center\"`` only after clearing/shifting the primary figure.
    """
    t = safe_text(text, font_size=font_size, color=color, max_width=11.5)
    if placement == "center":
        t.move_to(ORIGIN)
        scene.play(FadeIn(t, scale=0.92), run_time=0.55, rate_func=smooth)
        if hold > 0:
            scene.wait(hold)
        if park:
            parked = t.copy().scale(0.68)
            park_key_sentence(parked, side=park)
            scene.play(Transform(t, parked), run_time=0.85, rate_func=smooth)
            if board is not None:
                board.slots.pop("title", None)
                board.set_key(t, side=park)
                board.assert_clear()
        return t

    if placement == "bottom":
        t.move_to([0.0, BOTTOM_Y, 0.0])
    else:
        if t.width > 11.5:
            t.scale_to_fit_width(11.5)
        max_h = (KEY_BAND[1] - KEY_BAND[0]) * 0.92
        if t.height > max_h:
            t.scale_to_fit_height(max_h)
        t.move_to([0.0, sum(KEY_BAND) / 2, 0.0])
    scene.play(FadeIn(t, shift=DOWN * 0.08), run_time=0.55, rate_func=smooth)
    if hold > 0:
        scene.wait(hold)
    if park and placement == "key":
        parked = t.copy()
        park_key_sentence(parked, side=park)
        scene.play(Transform(t, parked), run_time=0.7, rate_func=smooth)
        if board is not None:
            board.slots.pop("title", None)
            board.set_key(t, side=park)
            board.assert_clear()
    elif board is not None:
        if placement == "bottom":
            board.slots["bottom"] = t
        else:
            board.slots.pop("title", None)
            board.slots["key"] = t
        board.assert_clear()
    return t


def labeled_box(
    label: str,
    width: float = 2.5,
    height: float = 1.0,
    color=BLUE_C,
    font_size: int = LABEL_SIZE,
) -> VGroup:
    rect = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.1,
        color=color,
        fill_opacity=0.2,
        stroke_width=2,
    )
    text = Text(label, font_size=font_size, color=color)
    if text.width > width - 0.3:
        text.scale_to_fit_width(width - 0.3)
    text.move_to(rect)
    return VGroup(rect, text)


# Re-export bands for scenes / tests
__all__ = [
    "C",
    "TITLE_SIZE",
    "SUBTITLE_SIZE",
    "BODY_SIZE",
    "LABEL_SIZE",
    "EQ_SIZE",
    "TITLE_Y",
    "BOTTOM_Y",
    "SAFE_WIDTH",
    "PANEL_LABEL_Y",
    "BAR_FLOOR_Y",
    "BAR_MAX_HEIGHT",
    "TITLE_BAND",
    "KEY_BAND",
    "PANEL_LABEL_BAND",
    "BOTTOM_BAND",
    "safe_text",
    "safe_multiline",
    "section_title",
    "bottom_note",
    "panel_label",
    "soft_idle",
    "breathe_until",
    "ask_about",
    "pop_named",
    "key_sentence",
    "labeled_box",
    "LayoutBoard",
    "mobject_box",
    "assert_no_overlaps",
    "assert_in_safe_frame",
    "collect_boxes",
]

def breathe_scene(scene, clock, cue: str, cadence: float = 1.1,
                  gap: float = 0.45, scale: float = 1.006) -> None:
    """Idle on whatever is currently on stage until a cue is nearly due.

    ``breathe_until`` must be handed the mobjects to move, which means knowing
    exactly what is alive at that instant. For a mid-beat cue several plays deep
    that is error-prone, and guessing wrong either crashes or animates the wrong
    thing. This breathes the scene's own top-level mobjects instead, with a
    ``there_and_back`` scale small enough to be imperceptible and self-reversing,
    so nothing drifts out of its reserved band.

    Use it wherever ``check_sync`` reports a still stretch: the report names the
    cue each stretch runs into, and that cue is the one to breathe up to.

    Args:
        scene: The running scene.
        clock: Anything exposing ``span_until`` — normally the ``TimedNarration``.
        cue: Cue to breathe up to.
        cadence: Length of one breath.
        gap: Silence deliberately left before the cue lands.
        scale: Breath amplitude; keep it tiny.
    """
    while True:
        remaining = float(clock.span_until(cue))
        if remaining <= gap + 0.2:
            return
        run = min(cadence, remaining - gap)
        if run < 0.25:
            return
        movers = [m for m in scene.mobjects
                  if isinstance(m, VMobject) and len(m.get_all_points())][:8]
        if not movers:
            scene.wait(run)
            continue
        scene.play(*[m.animate.scale(scale) for m in movers], run_time=run,
                   rate_func=there_and_back)
