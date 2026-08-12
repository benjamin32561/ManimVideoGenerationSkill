"""Layout overlap tests for manim-explain demos."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


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


DEMO = REPO / "demos" / "topk-on-mass"
sys.path.insert(0, str(_skill_scripts()))
sys.path.insert(0, str(DEMO))

from layout_check import (  # noqa: E402
    KEY_BAND,
    PANEL_LABEL_BAND,
    TITLE_BAND,
    Box,
    assert_in_safe_frame,
    assert_no_overlaps,
    boxes_overlap,
    collect_boxes,
    find_overlaps,
)


def test_aabb_detects_overlap():
    a = Box(0, 0, 1, 1, "a")
    b = Box(0.5, 0.5, 1.5, 1.5, "b")
    c = Box(2, 2, 3, 3, "c")
    assert boxes_overlap(a, b, pad=0.0)
    assert not boxes_overlap(a, c, pad=0.0)
    hits = find_overlaps([a, b, c], pad=0.0)
    assert len(hits) == 1


def test_aabb_pad_expands_collision():
    a = Box(0, 0, 1, 1, "a")
    b = Box(1.02, 0, 2, 1, "b")
    assert not boxes_overlap(a, b, pad=0.0)
    assert boxes_overlap(a, b, pad=0.05)


def test_reserved_bands_do_not_overlap():
    """Title / key / panel / bottom bands must be disjoint (architectural guard)."""
    bands = {
        "title": TITLE_BAND,
        "key": KEY_BAND,
        "panel": PANEL_LABEL_BAND,
        "bottom": (-3.55, -2.75),
    }
    names = list(bands)
    for i, n in enumerate(names):
        for m in names[i + 1 :]:
            lo_a, hi_a = bands[n]
            lo_b, hi_b = bands[m]
            overlap = not (hi_a <= lo_b or hi_b <= lo_a)
            assert not overlap, f"bands '{n}' and '{m}' overlap: {bands[n]} vs {bands[m]}"


def test_assert_no_overlaps_raises():
    with pytest.raises(AssertionError, match="overlap"):
        assert_no_overlaps(
            [Box(0, 0, 1, 1, "a"), Box(0.2, 0.2, 0.8, 0.8, "b")],
            pad=0.0,
        )


@pytest.mark.parametrize("name", [
    "cold_open",
    "question",
    "class_mean",
    "threshold",
    "gain_trap",
    "top_set",
    "formula_build",
    "read_baseline",
    "scale_invariance",
    "siblings",
    "settle",
])
def test_demo_layout_snapshots_no_overlap(name):
    if not DEMO.is_dir():
        pytest.skip(f"demo not present: {DEMO.name} (demos/ is gitignored)")
    # Import manim-backed snapshots lazily so pure tests stay light
    from utils.layout_snapshots import ALL_SNAPSHOTS  # noqa: WPS433

    items = ALL_SNAPSHOTS[name]()
    boxes = collect_boxes([(mob, lab) for lab, mob in items])
    try:
        assert_no_overlaps(boxes, pad=0.08)
        assert_in_safe_frame(boxes)
    except AssertionError as exc:
        raise AssertionError(f"snapshot '{name}' failed layout check:\n{exc}") from exc


CKA_DEMO = REPO / "demos" / "cka"
SELECTIVITY_DEMO = REPO / "demos" / "neuron-selectivity"
HATS_DEMO = REPO / "demos" / "axiom-of-choice-hats"


def _check_demo_snapshot(demo_dir, module_name, name):
    """Load a demo's layout snapshots in isolation and assert no overlaps.

    Each demo ships its own ``utils`` package, so cached modules are dropped
    before and after the import.

    Args:
        demo_dir: Path to ``demos/<slug>``.
        module_name: Unique module name for the loaded snapshot file.
        name: Snapshot key inside ``ALL_SNAPSHOTS``.

    Raises:
        AssertionError: If any tracked mobjects overlap or leave the safe frame.

    Skips when the demo directory is absent — ``demos/`` is gitignored, so a
    fresh clone of the skill has no demos to check.
    """
    import importlib.util

    snap_path = demo_dir / "utils" / "layout_snapshots.py"
    if not snap_path.is_file():
        pytest.skip(f"demo not present: {demo_dir.name} (demos/ is gitignored)")
    spec = importlib.util.spec_from_file_location(module_name, snap_path)
    assert spec and spec.loader
    sys.path.insert(0, str(demo_dir))
    for mod in list(sys.modules):
        if mod == "utils" or mod.startswith("utils."):
            del sys.modules[mod]
    try:
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        items = mod.ALL_SNAPSHOTS[name]()
        boxes = collect_boxes([(mob, lab) for lab, mob in items])
        assert_no_overlaps(boxes, pad=0.08)
        assert_in_safe_frame(boxes)
    except AssertionError as exc:
        raise AssertionError(
            f"{demo_dir.name} snapshot '{name}' failed layout check:\n{exc}"
        ) from exc
    finally:
        if str(demo_dir) in sys.path:
            sys.path.remove(str(demo_dir))
        for mod in list(sys.modules):
            if mod == "utils" or mod.startswith("utils.") or mod == module_name:
                del sys.modules[mod]
        # Restore topk demo for subsequent topk imports
        if str(DEMO) not in sys.path:
            sys.path.insert(0, str(DEMO))


@pytest.mark.parametrize("name", [
    "hook",
    "question",
    "match_lied",
    "flatten",
    "gram",
    "center",
    "cka_formula",
    "invariants",
    "settle",
])
def test_cka_layout_snapshots_no_overlap(name):
    _check_demo_snapshot(CKA_DEMO, "cka_layout_snapshots", name)


@pytest.mark.parametrize("name", [
    "hook",
    "question",
    "gallery",
    "rows",
    "dual_panel",
    "class_means",
    "index",
    "ablation",
    "settle",
])
def test_selectivity_layout_snapshots_no_overlap(name):
    _check_demo_snapshot(SELECTIVITY_DEMO, "selectivity_layout_snapshots", name)


@pytest.mark.parametrize("name", [
    "hook",
    "finite_trick",
    "infinite_counter",
    "infinite_question",
    "claim",
    "sequence",
    "equivalence",
    "axiom",
    "why_it_works",
    "catch",
    "settle",
])
def test_hats_layout_snapshots_no_overlap(name):
    _check_demo_snapshot(HATS_DEMO, "hats_layout_snapshots", name)
