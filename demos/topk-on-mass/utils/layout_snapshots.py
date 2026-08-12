"""Static layout snapshots for top-k on-mass — pytest overlap checks.

Each snapshot lists **everything text-like that is on screen at that beat**.
A snapshot that omits a co-present chip certifies a frame that never occurs.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from manim import *

DEMO_DIR = Path(__file__).resolve().parents[1]


def _skill_scripts() -> Path:
    """Find the manim-explain skill's ``scripts/`` directory.

    Honors ``MANIM_EXPLAIN_ROOT`` (exported by the skill's ``scripts/env.sh``),
    then searches the project and ``$HOME`` for an installed skill, so a demo
    keeps working wherever the skill is installed.

    Returns:
        Absolute path to the skill's ``scripts`` directory.

    Raises:
        FileNotFoundError: If the skill cannot be located.
    """
    env_root = os.environ.get("MANIM_EXPLAIN_ROOT")
    if env_root and (Path(env_root) / "scripts" / "layout_check.py").is_file():
        return Path(env_root) / "scripts"
    here = Path(__file__).resolve()
    for base in [*here.parents, Path.home()]:
        for rel in ("skills", ".claude/skills", ".cursor/skills", ".agents/skills"):
            candidate = base / rel / "manim-explain" / "scripts"
            if (candidate / "layout_check.py").is_file():
                return candidate
    raise FileNotFoundError(
        "Cannot locate the manim-explain skill. Set MANIM_EXPLAIN_ROOT or source "
        "the skill's scripts/env.sh."
    )


sys.path.insert(0, str(_skill_scripts()))
sys.path.insert(0, str(DEMO_DIR))

from layout_check import park_key_sentence  # noqa: E402
from utils.style import (  # noqa: E402
    C,
    EQ_SIZE,
    bottom_note,
    panel_label,
    safe_text,
    section_title,
)

# Mirror of the scene's below-axis chip strip
AXIS_Y = -1.15
CHIP_Y = -1.85
COUNTER_X = -4.6
GAIN_X = -1.7
F_X = 1.4
CUT_CHIP_X = 5.5
COL_X = 5.35
COL_H = 1.5

ON_EQ = (
    r"\mathrm{on\text{-}mass}(c)"
    r"=\frac{\sum_{j\in S_c}|\mu_{c,j}|}{\sum_{j=1}^{F}|\mu_{c,j}|}"
)


def _parked_key(text: str, side: str = "left") -> Text:
    """Key sentence as it sits after parking into KEY_BAND."""
    t = safe_text(text, font_size=int(34 * 0.68), color=C["accent"], max_width=7.5)
    return park_key_sentence(t, side=side)


def _chip(text: str, x: float, y: float = CHIP_Y, font_size: int = 22) -> VGroup:
    """Chip stand-in sized like the scene's pill (label plus padding)."""
    t = safe_text(text, font_size=font_size, color=C["label"])
    frame = RoundedRectangle(
        width=t.width + 0.34, height=t.height + 0.26, corner_radius=0.09, stroke_width=1.6
    )
    t.move_to(frame)
    return VGroup(frame, t).move_to([x, y, 0])


def _readout(value: str, x: float = COL_X, y: float = -1.75) -> VGroup:
    """Two-line on-mass readout stand-in."""
    name = safe_text("on-mass", font_size=18, color=C["label"])
    val = safe_text(value, font_size=26, color=C["gold"])
    body = VGroup(name, val).arrange(DOWN, buff=0.08)
    frame = RoundedRectangle(
        width=body.width + 0.38, height=body.height + 0.26, corner_radius=0.09, stroke_width=1.6
    )
    body.move_to(frame)
    return VGroup(frame, body).move_to([x, y, 0])


def _on_eq(font_delta: int = 10, y: float = -3.15) -> MathTex:
    """The named on-mass equation as parked in the bottom band."""
    return MathTex(ON_EQ, font_size=EQ_SIZE - font_delta).move_to([0.0, y, 0.0])


def _dist_lab() -> Text:
    """Panel label naming the on-screen object."""
    return panel_label("class-c response distribution", C["secondary"])


def snapshot_cold_open():
    """Title strip alone over the network."""
    return [("title", section_title("Top-k on-mass"))]


def snapshot_question():
    """Parked hook question with the input-side class tag."""
    key = _parked_key("who is carrying this class?")
    tag = safe_text("class c", font_size=20, color=C["accent"]).move_to([-5.55, 0.55, 0])
    return [("key", key), ("tag", tag)]


def snapshot_class_mean():
    """Class-mean definition under the distribution panel label."""
    eq = MathTex(
        r"\mu_{c,j}=\frac{1}{|\{m:\, y_m=c\}|}\sum_{m:\, y_m=c} a_j(m)",
        font_size=EQ_SIZE - 12,
    ).move_to([0.0, -3.15, 0.0])
    return [("dist_lab", _dist_lab()), ("mu_eq", eq)]


def snapshot_threshold():
    """Cutoff chip, on-counter and the magnitude label together."""
    cut_y = AXIS_Y + 0.30 * (1.35 / 0.92)
    eq = MathTex(r"|\mu_{c,j}|", font_size=EQ_SIZE - 4).move_to([0.0, -3.15, 0.0])
    return [
        ("dist_lab", _dist_lab()),
        ("counter", _chip("on: 9 / 20", COUNTER_X)),
        ("cut_chip", _chip("cutoff 0.30", CUT_CHIP_X, y=cut_y, font_size=20)),
        ("abs_eq", eq),
    ]


def snapshot_gain_trap():
    """Loud state: counter, gain chip, cutoff chip, key line and bottom note."""
    cut_y = AXIS_Y + 0.30 * (1.35 / 0.92)
    return [
        ("key", _parked_key("loudness, not concentration")),
        ("counter", _chip("on: 14 / 20", COUNTER_X)),
        ("gain", _chip("gain x1.8", GAIN_X)),
        ("cut_chip", _chip("cutoff 0.30", CUT_CHIP_X, y=cut_y, font_size=20)),
        ("note", bottom_note("same shape, louder", color=GREY_B)),
    ]


def snapshot_top_set():
    """Quota chip, the dead counter and the set-size equation."""
    eq = MathTex(r"|S_c| = fF", font_size=EQ_SIZE - 6).move_to([0.0, -3.15, 0.0])
    return [
        ("dist_lab", _dist_lab()),
        ("f_chip", _chip("f = 10%", F_X)),
        ("counter", _chip("on: 2 = fF, always", COUNTER_X)),
        ("set_eq", eq),
    ]


def snapshot_formula_build():
    """On-mass line, quota chip and the column readout are all on screen."""
    return [
        ("dist_lab", _dist_lab()),
        ("f_chip", _chip("f = 10%", F_X)),
        ("readout", _readout("0.26")),
        ("on_eq", _on_eq()),
    ]


def snapshot_read_baseline():
    """Baseline label on the column must clear the readout and the equation."""
    base = safe_text("uniform baseline = f", font_size=18, color=WHITE).move_to(
        [COL_X, AXIS_Y + COL_H + 0.42, 0]
    )
    return [
        ("dist_lab", _dist_lab()),
        ("f_chip", _chip("f = 10%", F_X)),
        ("base", base),
        ("readout", _readout("0.10")),
        ("on_eq", _on_eq()),
    ]


def snapshot_scale_invariance():
    """Count-vs-ratio comparison beside the gain chip, quota chip and readout."""
    compare = VGroup(
        safe_text("count: 9 → 14", font_size=18, color=C["wrong"]),
        safe_text("on-mass: 0.26 → 0.26", font_size=18, color=C["right"]),
    ).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
    compare.move_to([COUNTER_X, CHIP_Y - 0.05, 0])
    return [
        ("dist_lab", _dist_lab()),
        ("compare", compare),
        ("gain", _chip("gain x1.8", GAIN_X)),
        ("f_chip", _chip("f = 10%", F_X)),
        ("readout", _readout("0.26")),
        ("on_eq", _on_eq()),
    ]


def snapshot_siblings():
    """Three comparison cards plus the closing note."""
    cards = VGroup(
        *[
            RoundedRectangle(width=3.6, height=1.5, corner_radius=0.12, stroke_width=2)
            for _ in range(3)
        ]
    ).arrange(RIGHT, buff=0.45)
    cards.move_to(UP * 0.15)
    note = bottom_note("concentration and preference can move opposite ways", color=C["label"])
    return [
        ("card0", cards[0]),
        ("card1", cards[1]),
        ("card2", cards[2]),
        ("note", note),
    ]


def snapshot_settle():
    """Takeaway equation, key line and the reported (f, on-mass) pair."""
    key = _parked_key("a share of the mass — at a stated fraction")
    eq = MathTex(ON_EQ, font_size=EQ_SIZE - 6).move_to(UP * 0.75)
    note = bottom_note("report the pair:  f = 10%,  on-mass = 0.26", color=C["gold"])
    return [("key", key), ("eq", eq), ("note", note)]


ALL_SNAPSHOTS = {
    "cold_open": snapshot_cold_open,
    "question": snapshot_question,
    "class_mean": snapshot_class_mean,
    "threshold": snapshot_threshold,
    "gain_trap": snapshot_gain_trap,
    "top_set": snapshot_top_set,
    "formula_build": snapshot_formula_build,
    "read_baseline": snapshot_read_baseline,
    "scale_invariance": snapshot_scale_invariance,
    "siblings": snapshot_siblings,
    "settle": snapshot_settle,
}
