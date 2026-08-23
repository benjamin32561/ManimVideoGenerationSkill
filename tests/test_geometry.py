"""Geometry-pass helpers: occupancy leftovers, wireframes, contact sheets.

Pure tests first. The Manim integration test is skipped when the library is
not importable; it is the one that proves ``--geometry_only`` writes no MP4
and still records an overlap.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

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


def _manim_env(scripts: Path, extra: dict[str, str] | None = None) -> dict[str, str]:
    """Environment for a Manim subprocess that cannot inherit stills-only flags.

    Args:
        scripts: Skill scripts directory, prepended to ``PYTHONPATH``.
        extra: Optional overlay (``MANIM_STILL_*`` for named-time tests).

    Returns:
        A copy of ``os.environ`` with stills-only keys cleared unless ``extra``
        sets them.
    """
    env = {**os.environ, "PYTHONPATH": str(scripts)}
    for key in (
        "MANIM_STILL_TIMES",
        "MANIM_STILL_PLAYS",
        "MANIM_STILL_ONLY",
        "MANIM_STILL_STOP",
        "MANIM_STILL_DIR",
    ):
        env.pop(key, None)
    if extra:
        env.update(extra)
    return env


sys.path.insert(0, str(_skill_scripts()))

from occupancy import leftover_labels, leftover_records, presence_spans, sample_at, boundary_leftovers, motion_events  # noqa: E402
from scene_snapshot import (  # noqa: E402
    list_snapshot_times,
    nearest_snapshot,
    rasterize_times,
    save_snapshot,
)
from qa_frames import compose_contact_sheet, list_keyframes, select_sheet_frames  # noqa: E402
from keyframe_capture import slug_reason, CapturePolicy, GeometryCapture  # noqa: E402
from play_window import window_for_interval  # noqa: E402
from still_request import (  # noqa: E402
    StillRequest,
    parse_floats,
    times_from_plays,
    times_from_violations,
    times_from_cues,
)
from layout_watch import _opacity_of  # noqa: E402
from wireframe import draw_sample, manim_to_pixel  # noqa: E402


def _item(mob_id: int, label: str, t_box: tuple[float, float, float, float] | None = None) -> dict:
    """Build one occupancy item for tests.

    Args:
        mob_id: Fake mobject id.
        label: Human label.
        t_box: Optional AABB. Defaults to a unit box at the origin.

    Returns:
        An occupancy item dict.
    """
    box = list(t_box) if t_box is not None else [0.0, 0.0, 1.0, 1.0]
    return {"id": mob_id, "label": label, "kind": "text", "box": box}


class _FakeMob:
    """Minimal opacity surface for ``_opacity_of`` tests."""

    def __init__(self, fill: float = 0.0, stroke: float = 0.0, kids: list | None = None) -> None:
        self._fill = fill
        self._stroke = stroke
        self._kids = kids or []

    def get_fill_opacity(self) -> float:
        return self._fill

    def get_stroke_opacity(self) -> float:
        return self._stroke

    def get_family(self) -> list:
        return [self, *self._kids]


def test_faded_text_opacity_is_zero():
    assert _opacity_of(_FakeMob(fill=0.0, stroke=0.0)) == 0.0


def test_mathtex_parent_reads_glyph_opacity():
    glyph = _FakeMob(fill=1.0, stroke=0.0)
    parent = _FakeMob(fill=0.0, stroke=0.0, kids=[glyph])
    assert _opacity_of(parent) == 1.0


def test_presence_spans_track_first_and_last():
    samples = [
        {"t": 1.0, "items": [_item(1, "arrow")]},
        {"t": 5.0, "items": [_item(1, "arrow"), _item(2, "chip")]},
        {"t": 9.0, "items": [_item(2, "chip")]},
    ]
    spans = presence_spans(samples)
    assert spans[1]["first"] == 1.0
    assert spans[1]["last"] == 5.0
    assert spans[2]["first"] == 5.0
    assert spans[2]["last"] == 9.0


def test_title_band_is_not_reported_as_a_leftover():
    samples = [
        {"t": 1.0, "items": [_item(1, "A long title", (-2.0, 3.10, 2.0, 3.80))]},
        {"t": 95.0, "items": [_item(1, "A long title", (-2.0, 3.10, 2.0, 3.80))]},
    ]
    assert leftover_labels(samples, duration=100.0) == []
    samples = [
        {"t": 1.0, "items": [_item(1, "arrow")]},
        {"t": 50.0, "items": [_item(1, "arrow")]},
        {"t": 95.0, "items": [_item(1, "arrow")]},
    ]
    labels = leftover_labels(samples, duration=100.0)
    assert labels == ["arrow"]


def test_late_figure_is_not_a_leftover():
    samples = [
        {"t": 80.0, "items": [_item(1, "chip")]},
        {"t": 95.0, "items": [_item(1, "chip")]},
    ]
    assert leftover_labels(samples, duration=100.0) == []


def test_disposed_early_figure_is_not_a_leftover():
    samples = [
        {"t": 1.0, "items": [_item(1, "panel")]},
        {"t": 20.0, "items": [_item(1, "panel")]},
        {"t": 95.0, "items": []},
    ]
    assert leftover_labels(samples, duration=100.0) == []


def test_two_rectangles_are_not_merged_by_label():
    samples = [
        {"t": 1.0, "items": [_item(1, "Rectangle"), _item(2, "Rectangle")]},
        {"t": 95.0, "items": [_item(1, "Rectangle")]},
    ]
    records = leftover_records(samples, duration=100.0)
    assert len(records) == 1
    assert records[0]["id"] == 1


def test_sample_at_picks_the_nearest_time():
    samples = [
        {"t": 1.0, "items": []},
        {"t": 5.0, "items": [_item(1, "here")]},
        {"t": 9.0, "items": []},
    ]
    hit = sample_at(samples, 5.4)
    assert hit is not None
    assert hit["t"] == 5.0


def test_slug_reason_is_filesystem_safe():
    assert slug_reason("cue:ready list") == "cue:ready_list"
    assert slug_reason("") == "still"


def test_manim_to_pixel_puts_origin_at_the_image_centre():
    px, py = manim_to_pixel(0.0, 0.0, pixel_width=800, pixel_height=400)
    assert px == pytest.approx(400.0)
    assert py == pytest.approx(200.0)


def test_wireframe_png_is_written(tmp_path: Path):
    sample = {
        "t": 1.25,
        "items": [
            _item(1, "core 0", (-2.0, -1.0, 2.0, 1.0)),
        ],
    }
    dest = tmp_path / "wf.png"
    draw_sample(sample, dest)
    assert dest.is_file()
    assert dest.stat().st_size > 0


def test_contact_sheet_from_png_dir(tmp_path: Path):
    from PIL import Image

    frames_dir = tmp_path / "keyframes"
    frames_dir.mkdir()
    paths = []
    for i in range(3):
        path = frames_dir / f"{i:03d}_cue:beat{i}_1.0{i}s.png"
        Image.new("RGB", (80, 45), (i * 40, 20, 80)).save(path)
        paths.append(path)
    dest = frames_dir / "contact_sheet.png"
    compose_contact_sheet(paths, dest, cols=2, cell=(40, 24), caption=False)
    assert dest.is_file()
    sheet = Image.open(dest)
    assert sheet.size == (80, 48)


def test_select_sheet_frames_prefers_overlaps(tmp_path: Path):
    from PIL import Image

    frames_dir = tmp_path / "kf"
    frames_dir.mkdir()
    names = [
        "000_play-end_1.00s.png",
        "001_overlap_2.00s.png",
        "002_cue:alpha_3.00s.png",
        "003_play-end_4.00s.png",
    ]
    for name in names:
        Image.new("RGB", (8, 8), (10, 10, 10)).save(frames_dir / name)
    frames = list_keyframes(frames_dir)
    chosen = select_sheet_frames(frames, max_tiles=2)
    assert any("_overlap_" in p.name for p in chosen)
    assert len(chosen) <= 2


def test_capture_policy_caps_play_ends():
    policy = CapturePolicy(max_stills=72, max_play_ends=2, play_end_gap=1.0)
    kwargs = dict(n_stills=0, n_play_ends=0, last_t=-1.0, last_overlap_t=-1.0)
    assert policy.allow("play-end", 1.0, **kwargs)
    kwargs.update(n_stills=1, n_play_ends=2, last_t=1.0)
    assert not policy.allow("play-end", 5.0, **kwargs)
    assert policy.allow("overlap", 5.0, **{**kwargs, "n_stills": 72})


def test_capture_policy_keeps_cues_under_the_cap():
    policy = CapturePolicy(max_stills=3, cue_gap=0.1)
    assert policy.allow(
        "cue:a", 1.0, n_stills=0, n_play_ends=0, last_t=-1.0, last_overlap_t=-1.0
    )
    assert not policy.allow(
        "cue:b", 2.0, n_stills=3, n_play_ends=0, last_t=1.0, last_overlap_t=-1.0
    )


def test_boundary_leftover_rides_a_mass_fade():
    samples = [
        {"t": 1.0, "items": [_item(i, f"g{i}") for i in range(10)]},
        {"t": 15.0, "items": [_item(i, f"g{i}") for i in range(10)] + [_item(99, "arrow")]},
        {"t": 20.0, "items": [_item(i, f"g{i}") for i in range(4)] + [_item(99, "arrow")]},
        {"t": 23.0, "items": [_item(i, f"g{i}") for i in range(4)] + [_item(99, "arrow")]},
    ]
    rows = boundary_leftovers(samples, drop_frac=0.35, min_drop=4, survive=2.0)
    assert any(r["id"] == 99 for r in rows)
    assert not any(r["id"] < 10 for r in rows)


def test_motion_events_report_centre_shifts():
    samples = [
        {"t": 1.0, "items": [_item(1, "chip", (-1.0, -0.5, 0.0, 0.5))]},
        {"t": 1.2, "items": [_item(1, "chip", (1.0, -0.5, 2.0, 0.5))]},
        {"t": 1.4, "items": [_item(1, "chip", (1.05, -0.5, 2.05, 0.5))]},
    ]
    events = motion_events(samples, min_shift=0.15)
    assert len(events) == 1
    assert events[0]["id"] == 1
    assert events[0]["shift"] == pytest.approx(2.0, abs=0.01)


def test_nearest_snapshot_respects_max_dt(tmp_path: Path):
    import numpy as np

    demo = tmp_path / "snap"
    rec = [{"points": np.zeros((4, 3), dtype=np.float32), "fill": None, "stroke": None, "width": 1.0, "z": 0}]
    save_snapshot(demo, 10.00, rec)
    save_snapshot(demo, 10.50, rec)
    assert nearest_snapshot(demo, 10.10, max_dt=0.35).stem == "10.00"
    assert nearest_snapshot(demo, 10.40, max_dt=0.35).stem == "10.50"
    assert nearest_snapshot(demo, 12.00, max_dt=0.35) is None
    assert list_snapshot_times(demo) == [10.0, 10.5]


def test_play_window_covers_the_overlapping_plays():
    plays = [
        {"start": 0.0, "end": 1.0, "kind": "anim"},
        {"start": 1.0, "end": 5.0, "kind": "wait"},
        {"start": 5.0, "end": 8.0, "kind": "anim"},
        {"start": 8.0, "end": 12.0, "kind": "anim"},
    ]
    assert window_for_interval(plays, 6.0, 9.0, pad=0) == (2, 3)
    assert window_for_interval(plays, 6.0, 9.0, pad=1) == (1, 3)


def test_geometry_only_detects_overlap_and_writes_no_mp4(tmp_path: Path):
    """End-to-end: overlapping Text under --geometry_only.

    Skipped when Manim is not importable. This is the contract the inner loop
    is built on: interpolate, sample boxes, rasterize one still, no movie.
    """
    pytest.importorskip("manim")
    scripts = _skill_scripts()
    demo = tmp_path / "toy"
    (demo / "scenes").mkdir(parents=True)
    scene_path = demo / "scenes" / "toy.py"
    scene_path.write_text(
        f"""from pathlib import Path
import sys
sys.path.insert(0, {str(scripts)!r})
from manim import *
from layout_watch import watch_layout

DEMO_DIR = Path({str(demo)!r})

class OverlapToy(Scene):
    def construct(self):
        watch_layout(self, DEMO_DIR, sample_every=0.1, min_duration=0.2)
        a = Text("HELLO", font_size=96).shift(LEFT * 0.35)
        b = Text("WORLD", font_size=96).shift(RIGHT * 0.35)
        self.add(a, b)
        self.wait(0.8)
"""
    )
    media = tmp_path / "media"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "manim",
            "--geometry_only",
            "-ql",
            "--disable_caching",
            "--media_dir",
            str(media),
            str(scene_path),
            "OverlapToy",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=120,
        env=_manim_env(scripts),
    )
    assert result.returncode == 0, result.stderr[-2000:]
    assert not list(media.rglob("*.mp4"))
    viol_path = demo / "out" / "layout_violations.json"
    assert viol_path.is_file(), result.stdout[-1500:]
    viol = json.loads(viol_path.read_text())
    assert viol["violations"], viol
    occ = json.loads((demo / "out" / "occupancy.json").read_text())
    assert occ["n_samples"] >= 1
    item = occ["samples"][0]["items"][0]
    for key in ("opacity", "fill", "depth", "box", "label"):
        assert key in item
    assert "motion" in occ
    keyframes = list((demo / "out" / "keyframes").glob("*.png"))
    assert keyframes, "geometry-only overlap should capture at least one still"
    assert list_snapshot_times(demo), "geometry walk should dump mobject snapshots"


def test_hidden_address_does_not_count_as_a_cut(tmp_path: Path):
    """``set_opacity(0)`` labels (queue_card hex) must not raise box-cuts."""
    pytest.importorskip("manim")
    scripts = _skill_scripts()
    demo = tmp_path / "ghost"
    (demo / "scenes").mkdir(parents=True)
    scene_path = demo / "scenes" / "ghost.py"
    scene_path.write_text(
        f"""from pathlib import Path
import sys
sys.path.insert(0, {str(scripts)!r})
from manim import *
from layout_watch import watch_layout

DEMO_DIR = Path({str(demo)!r})

class GhostToy(Scene):
    def construct(self):
        watch_layout(self, DEMO_DIR, sample_every=0.1, min_duration=0.2)
        box = Rectangle(width=3.0, height=0.8)
        ghost = Text("0x0000", font_size=36).move_to(box.get_left())
        ghost.set_opacity(0.0)
        self.add(box, ghost)
        self.wait(0.6)
"""
    )
    media = tmp_path / "media"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "manim",
            "--geometry_only",
            "-ql",
            "--disable_caching",
            "--media_dir",
            str(media),
            str(scene_path),
            "GhostToy",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=120,
        env=_manim_env(scripts),
    )
    assert result.returncode == 0, result.stderr[-2000:]
    viol = json.loads((demo / "out" / "layout_violations.json").read_text())
    assert viol["violations"] == []
    occ = json.loads((demo / "out" / "occupancy.json").read_text())
    labels = [
        it["label"]
        for sample in occ["samples"]
        for it in sample.get("items") or []
    ]
    assert "0x0000" not in labels


def test_parse_floats_and_play_times():
    assert parse_floats("93.6, 367.8") == [93.6, 367.8]
    plays = [
        {"start": 0.0, "end": 1.0},
        {"start": 1.0, "end": 5.0},
    ]
    assert times_from_plays(plays, [1], at="end") == [5.0]
    assert times_from_plays(plays, [1], at="mid") == [3.0]


def test_times_from_violations_use_midpoints():
    payload = {
        "violations": [
            {"start": 10.0, "end": 12.0, "duration": 2.0, "midpoint": 11.0},
            {"start": 1.0, "end": 1.2, "duration": 0.2, "midpoint": 1.1},
        ]
    }
    assert times_from_violations(payload, min_duration=1.0) == [11.0]


def test_times_from_cues_prefer_bookmarks():
    timeline = {
        "bookmarks": {"ready": 4.5},
        "cues": [{"cue": "ready", "t": 4.5}, {"cue": "late", "t": 9.0}],
    }
    assert times_from_cues(timeline, ["ready", "late"]) == [4.5, 9.0]


def test_still_request_round_trips_through_env():
    req = StillRequest(times=[1.25, 8.0], plays=[3], still_only=True, stop_after=True)
    env = req.to_env()
    got = StillRequest.from_env(env)
    assert got.times == [1.25, 8.0]
    assert got.plays == [3]
    assert got.still_only is True
    assert got.stop_after is True
    assert got.due_times(1.25, got.times) == [1.25]
    assert got.next_time(0.4, 2.0, got.times) == 1.25
    assert got.next_time(1.3, 2.0, [1.25, 8.0]) is None


class _FakeRenderer:
    """Minimal ``capture_still`` surface for GeometryCapture tests."""

    num_plays = 1

    def capture_still(self, scene, dest, reason) -> None:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(b"PNG")


class _FakeScene:
    """Scene clock + renderer for named-time capture tests."""

    def __init__(self) -> None:
        self.time = 0.0
        self.renderer = _FakeRenderer()


def test_named_times_write_stills_and_stop(tmp_path: Path):
    scene = _FakeScene()
    request = StillRequest(
        times=[0.40, 1.20],
        still_only=True,
        stop_after=True,
        out_rel="out/stills",
    )
    capture = GeometryCapture(scene, tmp_path, request=request)
    scene.time = 0.40
    assert capture.tick(0.40) is False
    scene.time = 1.20
    assert capture.tick(1.20) is True
    pngs = list((tmp_path / "out" / "stills").glob("*.png"))
    assert len(pngs) == 2
    capture.flush()
    payload = json.loads((tmp_path / "out" / "stills" / "manifest.json").read_text())
    assert payload["missing"]["times"] == []
    assert [row["t"] for row in payload["stills"]] == [0.4, 1.2]


def test_stills_only_ignores_overlap_policy(tmp_path: Path):
    scene = _FakeScene()
    request = StillRequest(times=[0.5], still_only=True, stop_after=False)
    capture = GeometryCapture(scene, tmp_path, request=request)
    scene.time = 0.2
    assert capture.capture("overlap") is None
    assert capture.capture("cue:ready") is None
    assert list((tmp_path / "out" / "stills").glob("*.png")) == []


def test_stills_only_aborts_before_later_beats(tmp_path: Path):
    """A wait past the requested time must not execute later construct() code."""
    pytest.importorskip("manim")
    scripts = _skill_scripts()
    demo = tmp_path / "hold"
    (demo / "scenes").mkdir(parents=True)
    scene_path = demo / "scenes" / "hold.py"
    scene_path.write_text(
        f"""from pathlib import Path
import sys
sys.path.insert(0, {str(scripts)!r})
from manim import *
from layout_watch import watch_layout

DEMO_DIR = Path({str(demo)!r})

class HoldToy(Scene):
    def construct(self):
        watch_layout(self, DEMO_DIR, sample_every=0.1)
        self.add(Text("HOLD", font_size=48))
        self.wait(2.0)
        raise RuntimeError("should_not_reach")
"""
    )
    occ = demo / "out" / "occupancy.json"
    occ.parent.mkdir(parents=True, exist_ok=True)
    occ.write_text(json.dumps({"n_samples": 7, "sentinel": True}) + "\n")
    marker = occ.stat().st_mtime
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "manim",
            "--geometry_only",
            "-ql",
            "--disable_caching",
            "--media_dir",
            str(tmp_path / "media"),
            str(scene_path),
            "HoldToy",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=120,
        env=_manim_env(
            scripts,
            {
                "MANIM_STILL_TIMES": "0.40",
                "MANIM_STILL_ONLY": "1",
                "MANIM_STILL_STOP": "1",
                "MANIM_STILL_DIR": "out/stills",
            },
        ),
    )
    assert result.returncode == 0, result.stderr[-2000:] + result.stdout[-1500:]
    assert "should_not_reach" not in result.stderr
    pngs = list((demo / "out" / "stills").glob("*.png"))
    assert len(pngs) == 1, pngs
    assert "0.40s" in pngs[0].name
    assert not list((tmp_path / "media").rglob("*.mp4"))
    assert json.loads(occ.read_text())["sentinel"] is True
    assert occ.stat().st_mtime == marker
    assert not (demo / "out" / "keyframes").exists() or not list(
        (demo / "out" / "keyframes").glob("*.png")
    )


def test_stills_only_jump_keeps_finished_mobjects(tmp_path: Path):
    """Plays before the requested time jump to their end; the still must show them."""
    pytest.importorskip("manim")
    from PIL import Image

    scripts = _skill_scripts()
    demo = tmp_path / "jump"
    (demo / "scenes").mkdir(parents=True)
    scene_path = demo / "scenes" / "jump.py"
    scene_path.write_text(
        f"""from pathlib import Path
import sys
sys.path.insert(0, {str(scripts)!r})
from manim import *
from layout_watch import watch_layout

DEMO_DIR = Path({str(demo)!r})

class JumpToy(Scene):
    def construct(self):
        watch_layout(self, DEMO_DIR, sample_every=0.1)
        sq = Square(side_length=1.2, color=RED, fill_opacity=1.0).shift(LEFT * 2)
        self.play(FadeIn(sq), run_time=0.5)
        self.play(FadeIn(Circle().shift(RIGHT * 2)), run_time=0.5)
        self.wait(0.4)
"""
    )
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "manim",
            "--geometry_only",
            "-ql",
            "--disable_caching",
            "--media_dir",
            str(tmp_path / "media"),
            str(scene_path),
            "JumpToy",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=120,
        env=_manim_env(
            scripts,
            {
                "MANIM_STILL_TIMES": "1.20",
                "MANIM_STILL_ONLY": "1",
                "MANIM_STILL_STOP": "1",
                "MANIM_STILL_DIR": "out/stills",
            },
        ),
    )
    assert result.returncode == 0, result.stderr[-2000:] + result.stdout[-1500:]
    pngs = list((demo / "out" / "stills").glob("*.png"))
    assert len(pngs) == 1, pngs
    extrema = Image.open(pngs[0]).convert("RGB").getextrema()
    assert extrema[0][1] > 180 and extrema[1][1] < 120, (
        "jumped FadeIn(red square) never landed in the still"
    )


def test_mobject_copy_does_not_alias_points():
    pytest.importorskip("manim")
    from manim import Square

    original = Square()
    before = original.points.copy()
    clone = original.copy()
    clone.shift([2.0, 0.0, 0.0])
    assert (original.points == before).all()
    assert not (clone.points == original.points).all()


def test_rasterize_times_uses_snapshots_not_construct(tmp_path: Path):
    """A PNG from a snapshot must not require re-running construct()."""
    pytest.importorskip("manim")
    from PIL import Image

    scripts = _skill_scripts()
    demo = tmp_path / "snapwalk"
    (demo / "scenes").mkdir(parents=True)
    scene_path = demo / "scenes" / "snap.py"
    scene_path.write_text(
        f"""from pathlib import Path
import sys
sys.path.insert(0, {str(scripts)!r})
from manim import *
from layout_watch import watch_layout

DEMO_DIR = Path({str(demo)!r})

class SnapToy(Scene):
    def construct(self):
        watch_layout(self, DEMO_DIR, sample_every=0.1)
        self.add(Square(side_length=1.5, color=RED, fill_opacity=1.0))
        self.wait(0.8)
"""
    )
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "manim",
            "--geometry_only",
            "-ql",
            "--disable_caching",
            "--media_dir",
            str(tmp_path / "media"),
            str(scene_path),
            "SnapToy",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=120,
        env=_manim_env(scripts),
    )
    assert result.returncode == 0, result.stderr[-2000:]
    assert list_snapshot_times(demo)
    written, missing = rasterize_times(demo, [0.40], quality="ql", max_dt=0.4)
    assert missing == []
    assert written
    png = demo / written[0]["path"]
    assert png.is_file()
    extrema = Image.open(png).convert("RGB").getextrema()
    assert extrema[0][1] > 180, "snapshot still should show the red square"

