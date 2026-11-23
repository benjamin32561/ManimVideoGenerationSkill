"""Render a video in parallel, one worker per beat: ``render.py demos/<series>/<slug>``.

Refuses to run unless ``plan_check.py`` passed for the current plan. Each beat's clip is a
frame range of the same scene (see ``explain.scene``), rendered by its own process. A beat
whose digest (``explain.windows.beat_digest``) matches its existing clip is not rendered
again. New clips must come back with the digest the plan check predicted. The clips are
checked frame-exactly, joined without re-encoding, and the narration is added. Writes
``out/video.mp4`` and ``out/render.json``.

Workers draw on the CPU unless GPUs are named (``explain.device``).

Options:
    --workers N    concurrent workers (default 8)
    --threads T    CPU cores per worker (default 8)
    --gpus 2,3     draw on these GPUs instead, one worker per GPU at a time
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import argparse
import json
import subprocess
import time
from dataclasses import dataclass

from explain.device import Device, device_env, named_gpus
from explain.media import frame_count, join_with_audio
from explain.paths import SKILL_ROOT, Video
from explain.plan import Timeline, plan_digest
from explain.report import require_passed
from explain.styles import load_style
from explain.windows import beat_digest

DEFAULT_WORKERS = 8


@dataclass
class Job:
    """One beat's render: its frame range, clip, expected digest and process."""

    beat: str
    first: int
    stop: int
    clip: Path
    digest: str
    process: subprocess.Popen | None = None
    log: Path | None = None
    device: Device | None = None


def plan_jobs(video: Video, timeline: Timeline, windows: list[dict], fps: int) -> list[Job]:
    """Split the film into one frame range per beat, each with the digest its clip must have.

    Args:
        video: The video.
        timeline: Its resolved timeline (beats with start/end seconds).
        windows: The plan check's windows (start and digest of each).
        fps: Frame rate.

    Returns:
        The jobs, covering frames ``[0, round(duration × fps))`` exactly once.
    """
    total = round(timeline.duration * fps)
    edges = [round(b.start * fps) for b in timeline.beats] + [total]
    jobs = []
    for i, beat in enumerate(timeline.beats):
        clip = video.beats_dir / f"{i:02d}_{beat.id}.mp4"
        jobs.append(Job(beat.id, edges[i], edges[i + 1], clip, beat_digest(windows, edges[i], edges[i + 1], fps)))
    return jobs


def reusable(job: Job) -> bool:
    """Whether a beat's existing clip is current: rendered for the same digest, frames complete.

    Args:
        job: The job.

    Returns:
        True when the clip can be joined as it is.
    """
    done = Path(f"{job.clip}.done.json")
    if not (job.clip.is_file() and done.is_file()):
        return False
    return json.loads(done.read_text()).get("digest") == job.digest and frame_count(job.clip) == job.stop - job.first


def start(job: Job, video: Video, device: Device) -> None:
    """Launch a worker process for one job on a device, removing any stale clip first.

    Args:
        job: The job.
        video: The video.
        device: Where the worker draws.
    """
    done = Path(f"{job.clip}.done.json")
    for stale in (job.clip, done):
        stale.unlink(missing_ok=True)
    env = device_env(device)
    env["PYTHONPATH"] = str(SKILL_ROOT)
    job.device = device
    job.log = job.clip.with_suffix(".log")
    job.process = subprocess.Popen(
        [sys.executable, "-m", "explain.worker", str(video.dir), str(job.first), str(job.stop), str(job.clip)],
        env=env, stdout=job.log.open("w"), stderr=subprocess.STDOUT)


def finished(job: Job) -> dict:
    """Confirm a worker produced a complete clip of the beat the plan check saw.

    A worker that crashed after writing its clip and its ``.done.json`` (manimgx sometimes
    segfaults at exit) still counts, because the clip is verified frame by frame.

    Args:
        job: A job whose process has exited.

    Returns:
        The worker's ``.done.json`` record.

    Raises:
        RuntimeError: If the marker is missing, the clip has the wrong number of frames, or the
            worker rendered a different beat than the plan check predicted (code or plan
            changed since the check).
    """
    done = Path(f"{job.clip}.done.json")
    if not done.is_file():
        raise RuntimeError(f"Beat {job.beat} failed (exit {job.process.returncode}); see {job.log}")
    frames = frame_count(job.clip)
    if frames != job.stop - job.first:
        raise RuntimeError(f"Beat {job.beat}: {frames} frames, expected {job.stop - job.first}")
    record = json.loads(done.read_text())
    if record["digest"] != job.digest:
        raise RuntimeError(f"Beat {job.beat} rendered a different digest than plan_check.py saw; run it again")
    job.log.unlink(missing_ok=True)
    return record


def devices(gpus: str | None, workers: int, threads: int) -> list[Device]:
    """The devices workers draw on, one per concurrent worker slot.

    Args:
        gpus: Comma-separated GPU indices, or None for the CPU.
        workers: Concurrent workers on the CPU.
        threads: CPU cores per worker.

    Returns:
        One device per slot: each named GPU once, or ``workers`` CPU slots.
    """
    if gpus:
        return [Device(gpu=g) for g in named_gpus([int(i) for i in gpus.split(",")])]
    return [Device(threads=threads)] * workers


def main() -> None:
    """Render every changed beat in parallel, join all clips and add the narration.

    Raises:
        SystemExit: If the plan check is missing, failed or stale, or a beat fails.
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("video", help="demos/<series>/<slug>")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument("--threads", type=int, default=Device().threads)
    parser.add_argument("--gpus", help="comma-separated GPU indices (default: the CPU)")
    args = parser.parse_args()
    video = Video.at(args.video)
    style = load_style(video.style_name)
    digest = plan_digest(video, style)
    report = require_passed(video.plan_report, digest, "plan_check.py")
    timeline = Timeline.load(video.events)
    fps = style.canvas.fps
    jobs = plan_jobs(video, timeline, report["windows"], fps)
    video.beats_dir.mkdir(parents=True, exist_ok=True)
    keep = {j.clip.name for j in jobs} | {f"{j.clip.name}.done.json" for j in jobs}
    for stale in video.beats_dir.iterdir():
        if stale.name not in keep:
            stale.unlink()

    began = time.monotonic()
    records = {j.beat: json.loads(Path(f"{j.clip}.done.json").read_text()) for j in jobs if reusable(j)}
    pending = [j for j in jobs if j.beat not in records]
    free, running = devices(args.gpus, args.workers, args.threads), []
    where = ", ".join(sorted({d.label for d in free}))
    while pending or running:
        while pending and free:
            job = pending.pop(0)
            start(job, video, free.pop(0))
            running.append(job)
        time.sleep(0.2)
        for job in [j for j in running if j.process.poll() is not None]:
            running.remove(job)
            free.append(job.device)
            try:
                records[job.beat] = finished(job)
            except RuntimeError as err:
                for other in running:
                    other.process.kill()
                raise SystemExit(str(err)) from err
    join_with_audio([j.clip for j in jobs], video.narration_wav, video.rendered)
    total = round(timeline.duration * fps)
    frames = frame_count(video.rendered)
    if frames != total:
        raise SystemExit(f"Joined video has {frames} frames, expected {total}")
    seconds = round(time.monotonic() - began, 1)
    rendered = [j.beat for j in jobs if j.process]
    (video.out / "render.json").write_text(json.dumps({
        "digest": digest, "frames": frames, "seconds": seconds, "device": where,
        "rendered": rendered, "beats": records}, indent=1) + "\n")
    print(f"render {video.series}/{video.slug}: {frames} frames in {seconds} s; rendered {len(rendered)} of "
          f"{len(jobs)} beats on {where}, reused the rest")
    print(f"  {video.rendered}")


if __name__ == "__main__":
    main()
