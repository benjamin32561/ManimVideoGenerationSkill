"""Check a video's plan before rendering: ``plan_check.py demos/<series>/<slug>``.

Refuses to run unless ``voice.py`` voiced the current spoken words with the style's voice.

1. Validates ``script.yaml``, ``plan/layout.json`` and ``plan/events.yaml`` (structure, the
   action vocabulary, object lifecycles, one action per object per event).
2. Resolves every event's anchor phrase against the narration and writes ``plan/events.json``.
3. Static checks: text sizes, word budgets, capitals, reading time, texts entering together.
4. Runs the scene without drawing and samples geometry at every frame: clipping, the safe
   area, text on text, moving shapes or copies crossing labels, containers, colliding movers.
   Only windows it has not seen are sampled; the samples of unchanged windows are reused
   from ``out/probe/`` (``explain.windows``).
5. Runs ``manimgx inspect`` as a second opinion; its storyboard goes to ``out/inspect.png``.

Everything runs on the CPU (``explain.device``). Writes ``out/plan_check.json`` (tied to the
plan's digest, with every window's digest) and exits 1 when anything is an error.
``render.py`` refuses to run without a passing, current report.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import argparse
import os
import signal
import subprocess

from explain.checks import size_problems, timeline_problems
from explain.device import Device, device_env
from explain.paths import SKILL_ROOT, Video
from explain.plan import load_layout, load_raw_events, narration_digest, plan_digest, resolve_timeline, validate_events
from explain.probe import GeometryProbe, find_problems
from explain.problems import Problem
from explain.report import print_problems, require_passed, write_report
from explain.scene import VideoScene, configure
from explain.script import load_script
from explain.styles import load_style
from explain.timing import Transcript


def copy_endpoints(timeline_events: tuple, layout) -> dict[str, set[str]]:
    """For each event, the leaves its copies fly from and to (a flight may touch them).

    Args:
        timeline_events: The resolved events.
        layout: The layout plan.

    Returns:
        Event id → leaf ids of every ``copy_to``/``morph`` source and target in it.
    """
    ends: dict[str, set[str]] = {}
    for event in timeline_events:
        for action in event.actions:
            if action["action"] in ("copy_to", "morph"):
                ends.setdefault(event.id, set()).update(layout.leaves([action["source"], action["target"]]))
    return ends


def run_inspect(video: Video) -> tuple[int, str]:
    """Run ``manimgx inspect`` on the video and keep its report and storyboard.

    Args:
        video: The video.

    Returns:
        ``(exit code, report text)``; exit code 1 means it found layout problems, a negative
        code the signal that killed it.
    """
    env = device_env(Device())
    env.update({"EXPLAIN_VIDEO": str(video.dir), "PYTHONPATH": str(SKILL_ROOT)})
    done = subprocess.run(["manimgx", "inspect", str(SKILL_ROOT / "explain" / "inspect_entry.py"), "InspectedVideo",
                           "-o", str(video.out / "inspect.png")], env=env, capture_output=True, text=True)
    report = (done.stdout + done.stderr).strip()
    (video.out / "inspect.txt").write_text(report + "\n")
    return done.returncode, report


def main() -> None:
    """Run every plan check and write the report.

    Raises:
        SystemExit: 1 when the plan has errors; with a message when files are missing or the
            narration was voiced from other words or another voice.
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("video", help="demos/<series>/<slug>")
    args = parser.parse_args()
    os.environ.update(device_env(Device()))
    video = Video.at(args.video)
    style = load_style(video.style_name)
    script = load_script(video.script)
    require_passed(video.voice_report, narration_digest(script, style.voice), "voice.py")
    layout = load_layout(video.layout)
    raw_events = load_raw_events(video.events_source)
    transcript = Transcript.load(video.words)
    digest = plan_digest(video, style)
    video.out.mkdir(parents=True, exist_ok=True)

    structural = validate_events(raw_events, layout, style)
    if structural:
        problems = [Problem("invalid_events", "error", line) for line in structural]
        write_report(video.plan_report, digest, problems)
        print_problems("plan_check", problems)
        raise SystemExit(1)
    timeline = resolve_timeline(raw_events, script, transcript)
    timeline.save(video.events)

    problems = size_problems(layout, style) + timeline_problems(layout, timeline, transcript, style)
    configure(style)
    scene = VideoScene(video, style)
    probe = GeometryProbe(scene, style.canvas.fps, video.probe_cache)
    scene.render(frames=probe)
    samples = probe.samples()
    probe.prune()
    problems += find_problems(samples, layout, style.canvas.width, style.canvas.height,
                              copy_endpoints(timeline.events, layout))
    sampled = sum(fresh for _, fresh in probe.windows)
    code, inspect_report = run_inspect(video)
    if code not in (0, 1):
        how = f"killed by {signal.Signals(-code).name}" if code < 0 else f"exit code {code}"
        raise SystemExit(f"manimgx inspect failed ({how}):\n{inspect_report[-1500:] or '(no output)'}")
    if code == 1:
        problems.append(Problem("inspect", "warning", "manimgx inspect", detail="see out/inspect.txt and out/inspect.png"))
    write_report(video.plan_report, digest, problems, beats=[vars(b) for b in timeline.beats],
                 windows=scene.windows, samples=len(samples))
    print_problems(f"plan_check {video.series}/{video.slug}", problems)
    print(f"  probe: sampled {sampled} of {len(probe.windows)} windows (the others were unchanged since the last check)")
    if any(p.severity == "error" for p in problems):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
