"""Guards for data integrity and concurrency: timing, the parallel frame split, reuse of unchanged
windows and beats, the CPU device, the review gate.

Run: ``python -m pytest skills/manim-explain/explain/tests`` from the repository root.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import json
from dataclasses import replace
from itertools import pairwise

import numpy as np
import pytest
import yaml

from explain.device import NO_DRIVER, Device, device_env
from explain.paths import Video
from explain.plan import Event, Layout, Timeline, narration_digest, plan_digest
from explain.probe import Sample, load_samples, save_samples
from explain.report import digest_files, require_passed, write_report
from explain.script import Script, ScriptBeat
from explain.styles import Voice, load_style
from explain.timing import Beat, Transcript, Word, locate_beats, resolve_anchor, unheard_phrases
from explain.windows import Ledger, beat_digest
from render import plan_jobs
from review import deliver


def transcript(text: str, gap_after: dict[int, float] | None = None) -> Transcript:
    """A synthetic transcript: one word every 0.3 s, with optional pauses after some words.

    Args:
        text: Space-separated words.
        gap_after: Word index → extra silence after it (s).

    Returns:
        The transcript.
    """
    words, t = [], 0.0
    for i, w in enumerate(text.split()):
        words.append(Word(w, t, t + 0.25))
        t += 0.3 + (gap_after or {}).get(i, 0.0)
    return Transcript(tuple(words), t + 0.5)


def test_anchor_binds_next_occurrence_in_order() -> None:
    """A phrase spoken twice resolves to the occurrence after the previous anchor."""
    tr = transcript("the cell leaks then the cell leaks again")
    first = resolve_anchor("the cell leaks", tr, 0)
    second = resolve_anchor("the cell leaks", tr, first[0] + 1)
    assert first == (0, 2) and second == (4, 6)


def test_missing_anchor_fails_loudly() -> None:
    """An anchor that is not in the transcript stops the plan instead of binding elsewhere."""
    with pytest.raises(ValueError, match="not found"):
        resolve_anchor("never said", transcript("the cell leaks"), 0)


def test_anchor_matches_numbers_in_words_or_digits() -> None:
    """An anchor written in words binds to digits Whisper wrote, covering every word they span."""
    tr = transcript("it lands at about minus 89 millivolts")
    assert resolve_anchor("about minus eighty-nine millivolts", tr, 0) == (3, 6)
    assert resolve_anchor("a hundred and forty", transcript("roughly 140 inside"), 0) == (1, 1)


def test_dropped_speech_is_reported() -> None:
    """A stretch of script the transcript never heard is reported, not silently absorbed."""
    tr = transcript("potassium leaves the cell then it stops")
    script = [("a", "Potassium leaves the cell, and eventually the gradient is gone for good, then it stops.")]
    assert unheard_phrases(script, tr, 6) == [("a", "and eventually the gradient is gone for good")]


def test_beats_tile_the_narration_and_cut_in_pauses() -> None:
    """Beats cover [0, duration] without gaps; each cut falls inside the pause between beats,
    even when Whisper writes a number as digits."""
    tr = transcript("potassium leaves the cell 140 millimolar inside then it stops", gap_after={3: 0.8})
    beats = locate_beats([("a", "Potassium leaves the cell."), ("b", "One hundred forty millimolar inside, then it stops.")], tr)
    assert beats[0].start == 0.0 and beats[-1].end == tr.duration
    assert beats[0].end == beats[1].start
    assert tr.words[3].end < beats[0].end < tr.words[4].start


def test_parallel_jobs_cover_every_frame_once() -> None:
    """Beat workers split the film into contiguous frame ranges that cover it exactly once."""
    beats = (Beat("a", 0.0, 9.69, 0, 30), Beat("b", 9.69, 25.95, 31, 81), Beat("c", 25.95, 58.04, 82, 180))
    timeline = Timeline(58.04, beats, ())
    video = Video(Path("/nonexistent/series/slug"))
    jobs = plan_jobs(video, timeline, [{"event": "blank", "start": 0.0, "digest": "d"}], 30)
    assert jobs[0].first == 0 and jobs[-1].stop == round(58.04 * 30)
    assert all(a.stop == b.first for a, b in pairwise(jobs))
    assert all(j.stop > j.first for j in jobs)


def test_delivery_refuses_a_video_changed_after_review(tmp_path: Path) -> None:
    """The review gate is tied to the exact video file: a re-render after review blocks delivery.

    Args:
        tmp_path: pytest's temporary directory, used as the project root.
    """
    (tmp_path / ".env").write_text("")
    series = tmp_path / "demos" / "s"
    (series / "v" / "out").mkdir(parents=True)
    (series / "series.yaml").write_text(yaml.safe_dump({"title": "t", "style": "3b1b"}))
    (series / "v" / "script.yaml").write_text("title: t\n")
    video = Video.at(series / "v")
    video.rendered.write_bytes(b"reviewed render")
    digest = plan_digest(video, load_style("3b1b"))
    video.review_record.write_text(json.dumps({"digest": digest, "video": digest_files(video.rendered)}))
    video.rendered.write_bytes(b"different render")
    with pytest.raises(SystemExit, match="changed after the review"):
        deliver(video, digest)
    assert not video.delivery.exists()


def test_narration_older_than_the_script_is_refused(tmp_path: Path) -> None:
    """Audio voiced from other spoken words or another voice cannot pass the voice gate.

    Changing only ``show`` keeps the narration valid; changing one spoken word or the voice's
    delivery instruction makes ``plan_check.py`` refuse until ``voice.py`` runs again.

    Args:
        tmp_path: pytest's temporary directory, holding the voice report.
    """
    beat = ScriptBeat("b1", "hook", None, "u0", None, None, None, None, None, False,
                      "Picture a cell at rest.", "a membrane")
    script = Script("t", {}, (beat,))
    voice = Voice("model", "Charon", "calm", 24000, 4500)
    report = tmp_path / "voice.json"
    write_report(report, narration_digest(script, voice), [])

    shown = Script("t", {}, (replace(beat, show="a membrane, labelled"),))
    require_passed(report, narration_digest(shown, voice), "voice.py")
    reworded = Script("t", {}, (replace(beat, say="Picture a cell at rest, again."),))
    for digest in (narration_digest(reworded, voice), narration_digest(script, replace(voice, instructions="fast"))):
        with pytest.raises(SystemExit, match="voice.py"):
            require_passed(report, digest, "voice.py")


def window_digests(layout: Layout, events: list[Event]) -> list[str]:
    """The window digests of a plan, as the scene computes them (each play on time).

    Args:
        layout: The layout.
        events: The events, in order.

    Returns:
        The blank window's digest, then one per event.
    """
    ledger = Ledger(layout, "code")
    starts = [e.start for e in events] + [events[-1].end + 1]
    return [ledger.blank(starts[0])] + [ledger.window(e, t, nxt - t) for e, (t, nxt) in zip(events, pairwise(starts), strict=True)]


def test_windows_change_only_where_the_frames_do() -> None:
    """A motion-only edit changes its own window; a layout edit, every window from the object's first use.

    Nothing before an object's first use depends on its layout.
    """
    text = {"type": "text", "content": "A", "x": 100, "y": 100, "size": 40, "color": "white"}
    layout = Layout({"a": dict(text), "b": {**text, "content": "B"}}, {}, {}, {})
    events = [Event("e1", "x", 1.0, 1.5, "b1", ({"action": "write", "targets": ["a"]},)),
              Event("e2", "x", 3.0, 3.5, "b1", ({"action": "write", "targets": ["b"]},)),
              Event("e3", "x", 5.0, 5.5, "b1", ({"action": "move", "targets": ["a"], "to": [500, 100]},)),
              Event("e4", "x", 7.0, 7.5, "b1", ({"action": "recolor", "targets": ["b"], "color": "red"},))]
    base = window_digests(layout, events)

    arced = [*events[:2], replace(events[2], actions=({**events[2].actions[0], "arc": 0.9},)), events[3]]
    assert [x != y for x, y in zip(base, window_digests(layout, arced), strict=True)] == [0, 0, 0, 1, 0]

    moved_b = Layout({"a": dict(text), "b": {**text, "content": "B", "y": 300}}, {}, {}, {})
    assert [x != y for x, y in zip(base, window_digests(moved_b, events), strict=True)] == [0, 0, 1, 1, 1]


def test_probe_samples_round_trip_exactly(tmp_path: Path) -> None:
    """A window's stored samples load back unchanged, empty windows included.

    Args:
        tmp_path: pytest's temporary directory.
    """
    samples = [Sample(0.5, ["a", "~copy"], np.array([[1.0, 2.0, 3.5, 4.25], [5.0, 6.0, 7.0, 8.0]]),
                      np.array([False, True]), "e1"),
               Sample(0.5333333333, [], np.zeros((0, 4)), np.zeros(0, dtype=bool), "e1")]
    save_samples(samples, tmp_path / "w.npz")
    back = load_samples(tmp_path / "w.npz")
    assert [(s.t, s.ids, s.event) for s in back] == [(s.t, s.ids, s.event) for s in samples]
    assert all(np.array_equal(a.boxes, b.boxes) and np.array_equal(a.moving, b.moving)
               for a, b in zip(back, samples, strict=True))
    save_samples([], tmp_path / "empty.npz")
    assert load_samples(tmp_path / "empty.npz") == []


def test_beat_digest_follows_only_its_own_windows() -> None:
    """Changing one window re-renders the beats that show it, and only those."""
    windows = [{"start": 0.0, "digest": "blank"}, {"start": 2.0, "digest": "w1"}, {"start": 12.0, "digest": "w2"}]
    beats = [(0, 300), (300, 600)]
    before = [beat_digest(windows, a, b, 30) for a, b in beats]
    windows[2]["digest"] = "w2 edited"
    after = [beat_digest(windows, a, b, 30) for a, b in beats]
    assert before[0] == after[0] and before[1] != after[1]


def test_cpu_device_hides_every_gpu() -> None:
    """A CPU process sees no Vulkan driver and none of the GPU-selection variables."""
    env = device_env(Device(threads=4))
    assert env["VK_ICD_FILENAMES"] == str(NO_DRIVER) and not NO_DRIVER.exists()
    assert env["LP_NUM_THREADS"] == "4" and env["EXPLAIN_DEVICE"] == "cpu"
    assert not {"VK_INSTANCE_LAYERS", "EXPLAIN_VK_PCI_BUS", "CUDA_VISIBLE_DEVICES"} & set(env)

