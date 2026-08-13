"""Tests for the motion and layout audits.

These cover the pure logic — overlap geometry, wait-vs-motion accounting, and
the spoken-change-word check — so the tools can be trusted without a render.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _skill_scripts() -> Path:
    """Find the manim-explain skill's ``scripts/`` directory.

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
    raise FileNotFoundError("Cannot locate the manim-explain skill scripts")


sys.path.insert(0, str(_skill_scripts()))

from check_sync import analyse, motion_in_window  # noqa: E402
from layout_watch import _overlap_fraction  # noqa: E402
from lint_script import visual_coverage  # noqa: E402


# ── layout geometry ──────────────────────────────────────────────────────────

def test_overlap_fraction_disjoint_boxes():
    assert _overlap_fraction((0, 0, 1, 1), (2, 2, 3, 3)) == 0.0


def test_overlap_fraction_is_relative_to_the_smaller_box():
    # small box fully inside a large one → completely obscured
    assert _overlap_fraction((0, 0, 10, 10), (1, 1, 2, 2)) == 1.0


def test_overlap_fraction_ignores_a_hairline_graze():
    # 1% of the smaller box — the kind of touch that is invisible on screen
    frac = _overlap_fraction((0, 0, 1, 1), (0.99, 0, 2, 1))
    assert 0 < frac < 0.05


# ── motion accounting ────────────────────────────────────────────────────────

def test_waits_never_count_as_motion():
    """Manim records Scene.wait as play(Wait); it must not mask a silent cue."""
    plays = [{"start": 0.0, "end": 5.0, "kind": "wait"}]
    assert motion_in_window(plays, 1.0, 4.0) == []


def test_real_animation_counts_as_motion():
    plays = [{"start": 1.0, "end": 2.0, "kind": "anim"}]
    assert len(motion_in_window(plays, 0.5, 3.0)) == 1


def test_silent_cue_is_reported():
    timeline = {
        "duration": 10.0,
        "cues": [{"cue": "alpha", "t": 1.0}, {"cue": "beta", "t": 5.0}],
        "plays": [
            {"start": 1.0, "end": 2.0, "kind": "anim"},
            {"start": 5.0, "end": 9.0, "kind": "wait"},
        ],
    }
    report = analyse(timeline, {"beta": "some_beat"}, min_motion=0.25, max_gap=6.0)
    silent = {e["cue"] for e in report["silent"]}
    assert silent == {"beta"}
    assert report["silent"][0]["beat"] == "some_beat"


def test_thin_cue_is_distinguished_from_silent():
    timeline = {
        "duration": 10.0,
        "cues": [{"cue": "alpha", "t": 1.0}, {"cue": "beta", "t": 5.0}],
        "plays": [{"start": 1.0, "end": 1.08, "kind": "anim"}],
    }
    report = analyse(timeline, {}, min_motion=0.25, max_gap=20.0)
    assert [e["cue"] for e in report["thin"]] == ["alpha"]
    assert [e["cue"] for e in report["silent"]] == ["beta"]


# ── spoken change-words vs show notes ────────────────────────────────────────

def test_narrated_change_without_matching_show_is_flagged():
    missing = visual_coverage(
        say="The bars grow taller and the gap collapses.",
        show="The chart is centred with a label above it.",
    )
    assert "grow" in " ".join(missing)


def test_show_describing_the_same_motion_passes():
    assert visual_coverage(
        say="The bars grow taller.",
        show="STAGED: each bar grows to its new height.",
    ) == []


def test_synonyms_are_accepted_so_the_check_is_not_noise():
    # "chop" in the VO, "sliced" in the notes — same motion, different word
    assert visual_coverage(
        say="You chop the energy into equal elements.",
        show="STAGED: the bar is sliced into equal elements.",
    ) == []
