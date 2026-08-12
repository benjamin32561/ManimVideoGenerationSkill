"""Static layout snapshots for the neuron-selectivity demo — pytest overlap checks."""

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

BAR_FLOOR = -1.70
H_SCALE = 1.35


def _parked_key(text: str, side: str = "left") -> Text:
    """Key sentence parked in KEY_BAND, as the scene parks it."""
    t = safe_text(text, font_size=26, color=C["highlight"], max_width=7.5)
    return park_key_sentence(t, side=side)


def snapshot_hook():
    """Title + response meter label while the net owns the stage."""
    title = section_title("Neuron Selectivity")
    meter = panel_label("response", C["gold"], x=3.9)
    return [("title", title), ("meter_lab", meter)]


def snapshot_question():
    """Parked hook question next to the meter label."""
    key = _parked_key("a dog neuron?")
    meter = panel_label("response", C["gold"], x=3.9)
    return [("key", key), ("meter_lab", meter)]


def snapshot_gallery():
    """Dataset / top-9 panel labels plus the parked question."""
    key = _parked_key("case closed?")
    data = panel_label("the dataset", C["dim"], x=-3.1)
    gal = panel_label("top 9", C["gold"], x=3.15)
    return [("key", key), ("data_lab", data), ("gal_lab", gal)]


def snapshot_rows():
    """Row-split view: axis caption + input-label caption + parked question."""
    key = _parked_key("what should selective look like?")
    ax_lab = safe_text("activation", font_size=20, color=C["dim"]).move_to([0.15, -2.32, 0])
    in_lab = safe_text("input label", font_size=18, color=C["label"]).move_to([-3.3, 1.65, 0])
    return [("key", key), ("ax_lab", ax_lab), ("in_lab", in_lab)]


def snapshot_dual_panel():
    """Selective / mixed panel labels + bottom caption."""
    sel = panel_label("selective", C["gold"], x=-3.3)
    mix = panel_label("mixed", C["wrong"], x=3.3)
    note = bottom_note("two units — same dataset", color=C["label"])
    return [("lab_sel", sel), ("lab_mix", mix), ("note", note)]


def snapshot_class_means():
    """Bar labels above the two bars while the definition sits in BOTTOM."""
    lab_max = MathTex(r"\mu_{\max}", font_size=30, color=C["gold"]).move_to(
        [-0.5, BAR_FLOOR + 0.84 * H_SCALE + 0.3, 0]
    )
    lab_rest = MathTex(r"\mu_{-\max}", font_size=30, color=C["dim"]).move_to(
        [0.5, BAR_FLOOR + 0.22 * H_SCALE + 0.3, 0]
    )
    eq = MathTex(
        r"\mu_{-\max} = \mathrm{mean}_{c\neq\max}\, \mu_c", font_size=EQ_SIZE - 8
    ).move_to([0.0, -3.15, 0])
    bars_lab = panel_label("favourite class vs. the rest", C["label"], x=0.0)
    return [("lab_max", lab_max), ("lab_rest", lab_rest), ("eq", eq), ("bars_lab", bars_lab)]


def snapshot_index():
    """Selectivity index in BOTTOM with the loudness key line parked."""
    key = _parked_key("same shape — just louder")
    eq = MathTex(
        r"\mathrm{SI} = \frac{\mu_{\max}-\mu_{-\max}}{\mu_{\max}+\mu_{-\max}}",
        font_size=EQ_SIZE - 6,
    ).move_to([0.0, -3.15, 0])
    gap_chip = VGroup(
        safe_text("raw gap", font_size=19, color=C["wrong"]),
        safe_text("1.36", font_size=26, color=C["wrong"]),
    ).arrange(DOWN, buff=0.1).move_to([-4.4, 0.45, 0])
    bars_lab = panel_label("favourite class vs. the rest", C["label"], x=0.0)
    # loudest moment: mu_max label rides the tallest bar
    lab_max = MathTex(r"\mu_{\max}", font_size=30, color=C["gold"]).move_to(
        [-0.5, BAR_FLOOR + 0.84 * 2.2 * H_SCALE + 0.3, 0]
    )
    return [
        ("key", key),
        ("eq", eq),
        ("gap_chip", gap_chip),
        ("bars_lab", bars_lab),
        ("lab_max", lab_max),
    ]


def snapshot_ablation():
    """Accuracy panel label + importance caption."""
    acc = panel_label("accuracy", C["right"], x=2.0)
    note = bottom_note("selective is not the same as relied upon", color=C["wrong"])
    return [("acc_lab", acc), ("note", note)]


def snapshot_settle():
    """Takeaway formula, parked question, closing caption."""
    key = _parked_key("one class high, the rest low?")
    eq = MathTex(
        r"\mathrm{SI} = \frac{\mu_{\max}-\mu_{-\max}}{\mu_{\max}+\mu_{-\max}}",
        font_size=EQ_SIZE,
    ).move_to([0.0, 0.8, 0])
    note = bottom_note(
        "what the unit responds to — not what the network reads", color=C["accent"]
    )
    return [("key", key), ("eq", eq), ("note", note)]


ALL_SNAPSHOTS = {
    "hook": snapshot_hook,
    "question": snapshot_question,
    "gallery": snapshot_gallery,
    "rows": snapshot_rows,
    "dual_panel": snapshot_dual_panel,
    "class_means": snapshot_class_means,
    "index": snapshot_index,
    "ablation": snapshot_ablation,
    "settle": snapshot_settle,
}
