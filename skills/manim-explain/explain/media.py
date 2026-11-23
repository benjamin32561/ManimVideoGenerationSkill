"""ffmpeg helpers: encoding raw frames, joining clips, muxing the narration, probing, frames.

Every video the pipeline writes is H.264 (yuv420p, CRF 18) at the style's constant frame
rate, so clips join without re-encoding.
"""

import json
import subprocess
import tempfile
from collections.abc import Iterator
from pathlib import Path

import numpy as np

CRF = "18"
PRESET = "medium"


def run(args: list[str]) -> str:
    """Run an ffmpeg-family command and fail loudly on error.

    Args:
        args: The command line.

    Returns:
        Its standard output.

    Raises:
        RuntimeError: With the command's stderr if it exits non-zero.
    """
    done = subprocess.run(args, capture_output=True, text=True)
    if done.returncode != 0:
        raise RuntimeError(f"{args[0]} failed: {done.stderr[-1200:]}")
    return done.stdout


def open_encoder(path: Path, width: int, height: int, fps: int) -> subprocess.Popen:
    """Start an ffmpeg process that encodes raw RGBA frames from its stdin to an MP4.

    Args:
        path: The MP4 to write.
        width: Frame width (px).
        height: Frame height (px).
        fps: Frame rate.

    Returns:
        The process; write ``width * height * 4`` bytes per frame to its stdin, then close it.
    """
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    return subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba",
         "-s", f"{width}x{height}", "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", PRESET,
         "-crf", CRF, "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(path)],
        stdin=subprocess.PIPE, stderr=subprocess.PIPE)


def frame_count(path: Path) -> int:
    """Count a video's frames exactly, by counting its packets (one per frame in an MP4).

    Reading packets skips decoding, so a 10-minute video is counted in a fraction of a second.

    Args:
        path: The video.

    Returns:
        The number of video frames.
    """
    out = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets",
               "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", str(path)])
    return int(out.strip())


def duration(path: Path) -> float:
    """A media file's duration in seconds.

    Args:
        path: Audio or video file.

    Returns:
        The container duration.
    """
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)])
    return float(json.loads(out)["format"]["duration"])


def join_with_audio(clips: list[Path], audio: Path, dest: Path) -> None:
    """Join clips without re-encoding and add the narration as AAC.

    Args:
        clips: Clips in order, all with identical codec settings.
        audio: The narration.
        dest: The finished video.
    """
    with tempfile.NamedTemporaryFile("w", suffix=".txt", dir=Path(dest).parent, delete=False) as listing:
        listing.write("".join(f"file '{Path(c).resolve()}'\n" for c in clips))
    try:
        run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", listing.name,
             "-i", str(audio), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac",
             "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(dest)])
    finally:
        Path(listing.name).unlink()


def encode_pcm(pcm: bytes, rate: int, dest: Path, bitrate: str | None = None) -> None:
    """Encode raw 16-bit mono PCM to an audio file; the extension picks the format.

    Args:
        pcm: The samples.
        rate: Sample rate (Hz).
        dest: The file to write (``.wav`` or ``.mp3``).
        bitrate: Compressed bitrate (e.g. ``96k``); None for the encoder's default.

    Raises:
        RuntimeError: If ffmpeg fails.
    """
    Path(dest).parent.mkdir(parents=True, exist_ok=True)
    args = ["ffmpeg", "-y", "-loglevel", "error", "-f", "s16le", "-ar", str(rate), "-ac", "1", "-i", "-"]
    args += ["-b:a", bitrate] if bitrate else []
    done = subprocess.run([*args, str(dest)], input=pcm, capture_output=True)
    if done.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {done.stderr.decode()[-800:]}")


def extract_frame(video: Path, t: float, dest: Path) -> None:
    """Save the frame shown at a time as a PNG.

    Args:
        video: The video.
        t: Time (s).
        dest: The PNG to write.
    """
    Path(dest).parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1", str(dest)])


def small_gray_frames(video: Path, width: int, height: int, first: int = 0, count: int | None = None,
                      fps: int = 1) -> Iterator[np.ndarray]:
    """Decode a video, or a stretch of it, as small grayscale frames, one array per frame.

    Args:
        video: The video.
        width: Width to scale to (px).
        height: Height to scale to (px).
        first: First frame to decode (the decoder seeks to half a frame before it, so exactly
            this frame comes first).
        count: How many frames to decode (None: to the end).
        fps: The video's frame rate (converts ``first`` to a seek time).

    Yields:
        ``(height, width)`` uint8 arrays, in frame order.
    """
    seek = ["-ss", f"{max(first - 0.5, 0) / fps:.6f}"] if first else []
    limit = ["-frames:v", str(count)] if count is not None else []
    proc = subprocess.Popen(["ffmpeg", "-loglevel", "error", *seek, "-i", str(video), "-vf", f"scale={width}:{height}",
                             *limit, "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
    size = width * height
    try:
        while chunk := proc.stdout.read(size):
            if len(chunk) < size:
                break
            yield np.frombuffer(chunk, dtype=np.uint8).reshape(height, width)
    finally:
        proc.stdout.close()
        proc.wait()
