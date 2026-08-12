"""Static layout snapshots for CKA v2 — pytest overlap checks."""

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
    PANEL_LABEL_Y,
    bottom_note,
    panel_label,
    safe_text,
    section_title,
)


def _parked_key(text: str, side: str = "left") -> Text:
    t = safe_text(text, font_size=int(34 * 0.68), color=C["accent"], max_width=7.5)
    return park_key_sentence(t, side=side)


def snapshot_hook():
    title = section_title("Centered Kernel Alignment")
    lab_a = panel_label("Net A", C["primary"], x=-3.3)
    lab_b = panel_label("Net B", C["secondary"], x=3.3)
    return [("title", title), ("lab_a", lab_a), ("lab_b", lab_b)]


def snapshot_question():
    key = _parked_key("Do they represent the world the same way?")
    lab_a = panel_label("Net A", C["primary"], x=-3.3)
    lab_b = panel_label("Net B", C["secondary"], x=3.3)
    return [("key", key), ("lab_a", lab_a), ("lab_b", lab_b)]


def snapshot_match_lied():
    lab_a = panel_label("Net A", C["primary"], x=-3.0)
    lab_b = panel_label("Net B", C["secondary"], x=3.0)
    ghost = bottom_note("same geometry — different bookkeeping", color=C["wrong"])
    return [("lab_a", lab_a), ("lab_b", lab_b), ("ghost", ghost)]


def snapshot_flatten():
    key = _parked_key("loses example geometry")
    return [("key", key)]


def snapshot_gram():
    pl_k = panel_label("K  (X)", C["primary"], x=-3.2)
    pl_l = panel_label("L  (Y)", C["secondary"], x=3.2)
    gram = MathTex(r"K_{ij} = \langle x_i,\, x_j\rangle", font_size=EQ_SIZE - 4)
    gram.move_to([0.0, -3.15, 0.0])
    return [("pl_k", pl_k), ("pl_l", pl_l), ("gram", gram)]


def snapshot_center():
    key = _parked_key("center")
    pl_k = MathTex(r"\tilde{K}", font_size=36, color=C["primary"]).move_to(
        LEFT * 3.2 + UP * PANEL_LABEL_Y
    )
    pl_l = MathTex(r"\tilde{L}", font_size=36, color=C["secondary"]).move_to(
        RIGHT * 3.2 + UP * PANEL_LABEL_Y
    )
    eq = MathTex(
        r"\tilde{K} = HKH",
        r"\quad",
        r"H = I - \tfrac{1}{n}11^{\top}",
        font_size=EQ_SIZE - 8,
    )
    eq.move_to([0.0, -3.15, 0.0])
    return [("key", key), ("pl_k", pl_k), ("pl_l", pl_l), ("eq", eq)]


def snapshot_cka_formula():
    key = _parked_key("normalize away loudness")
    eq = MathTex(
        r"\mathrm{CKA}(K,L)"
        r"="
        r"\frac{\mathrm{HSIC}(K,L)}"
        r"{\sqrt{\mathrm{HSIC}(K,K)\,\mathrm{HSIC}(L,L)}}",
        font_size=EQ_SIZE - 8,
    )
    eq.move_to([0.0, -3.15, 0.0])
    return [("key", key), ("eq", eq)]


def snapshot_invariants():
    key = _parked_key("invariant to orthogonal transforms")
    note = bottom_note("1-to-1 would have collapsed — CKA holds", color=C["right"])
    return [("key", key), ("note", note)]


def snapshot_settle():
    key = _parked_key("same example geometry?")
    eq = MathTex(
        r"\mathrm{CKA}(K,L)"
        r"="
        r"\frac{\langle\tilde{K},\,\tilde{L}\rangle_F}"
        r"{\|\tilde{K}\|_F\,\|\tilde{L}\|_F}",
        font_size=EQ_SIZE - 4,
    )
    eq.move_to(UP * 0.6)
    note = bottom_note("after centering — and after normalizing loudness", color=C["accent"])
    return [("key", key), ("eq", eq), ("note", note)]


ALL_SNAPSHOTS = {
    "hook": snapshot_hook,
    "question": snapshot_question,
    "match_lied": snapshot_match_lied,
    "flatten": snapshot_flatten,
    "gram": snapshot_gram,
    "center": snapshot_center,
    "cka_formula": snapshot_cka_formula,
    "invariants": snapshot_invariants,
    "settle": snapshot_settle,
}
