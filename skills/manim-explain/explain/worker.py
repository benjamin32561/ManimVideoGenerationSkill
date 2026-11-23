"""Render one beat's frame range of a video: ``python -m explain.worker <video> <first> <stop> <clip>``.

Started by ``scripts/render.py``, one process per beat, each sent to the CPU or to one GPU
through its environment (``explain.device.device_env``). It checks it landed there, runs the
whole scene but draws and encodes only frames ``[first, stop)``, then writes
``<clip>.done.json``: the device, the time, and the digest of the beat it rendered
(``explain.windows.beat_digest``), so the orchestrator can tell a finished, current clip from
a crashed process or a clip of an older plan.
"""

import json
import sys
import time
from pathlib import Path

from explain.device import check_adapter
from explain.paths import Video
from explain.scene import BeatRecorder, VideoScene, configure
from explain.styles import load_style
from explain.windows import beat_digest


def main() -> None:
    """Render the requested frame range and record how it went.

    Raises:
        SystemExit: On wrong arguments.
        RuntimeError: If manimgx is not drawing on the device this worker was sent to.
    """
    if len(sys.argv) != 5:
        raise SystemExit("usage: python -m explain.worker <video_dir> <first_frame> <stop_frame> <clip.mp4>")
    video = Video.at(sys.argv[1])
    first, stop, clip = int(sys.argv[2]), int(sys.argv[3]), Path(sys.argv[4])
    adapter = check_adapter()
    style = load_style(video.style_name)
    configure(style)
    began = time.monotonic()
    recorder = BeatRecorder(first, stop, clip, style)
    scene = VideoScene(video, style)
    scene.render(frames=recorder)
    padded = recorder.close()
    Path(f"{clip}.done.json").write_text(json.dumps({
        "first": first, "stop": stop, "padded": padded, "adapter": adapter,
        "digest": beat_digest(scene.windows, first, stop, style.canvas.fps),
        "seconds": round(time.monotonic() - began, 2)}))


if __name__ == "__main__":
    main()
