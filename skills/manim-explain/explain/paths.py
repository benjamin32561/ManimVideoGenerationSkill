"""Where the skill, the project and a video's files live.

The skill is portable: it may sit in this repo under ``skills/manim-explain/``, in
``~/.claude/skills/``, ``~/.cursor/skills/`` or a plugin cache. Videos live in the user's
project, a different tree::

    <project>/demos/<series>/series.yaml          style + title of the series
    <project>/demos/<series>/<slug>/script.yaml    the narrated script
    <project>/demos/<series>/<slug>/audio/         narration.wav, narration.mp3, words.json
    <project>/demos/<series>/<slug>/plan/          layout.json, events.yaml, events.json
    <project>/demos/<series>/<slug>/custom.py      optional video-specific components
    <project>/demos/<series>/<slug>/out/           check reports, beat clips, video, review frames
    <project>/output_videos/<series>/<slug>.mp4    the delivered video

Nothing here hard-codes an install path.
"""

import os
from dataclasses import dataclass
from pathlib import Path

import yaml

SKILL_ROOT = Path(__file__).resolve().parent.parent


def find_project_root(start: Path) -> Path:
    """Find the root of the user's project: the nearest ancestor holding ``.git`` or ``.env``.

    Args:
        start: A path inside the project, typically a video directory.

    Returns:
        The project root.

    Raises:
        FileNotFoundError: If no ancestor of ``start`` holds ``.git`` or ``.env``.
    """
    start = Path(start).resolve()
    for candidate in (start, *start.parents):
        if (candidate / ".git").exists() or (candidate / ".env").is_file():
            return candidate
    raise FileNotFoundError(f"No project root (.git or .env) above {start}")


def load_dotenv(project_root: Path) -> None:
    """Load ``KEY=value`` pairs from the project's ``.env`` into the environment.

    Variables already exported win over the file, so a shell export overrides it.

    Args:
        project_root: The directory that may hold a ``.env`` file. A missing file is not an
            error here; the caller that needs a key reports it.
    """
    env_path = Path(project_root) / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


@dataclass(frozen=True)
class Video:
    """One video of a series and every file the pipeline reads or writes for it.

    Attributes:
        dir: ``<project>/demos/<series>/<slug>``.
    """

    dir: Path

    @classmethod
    def at(cls, path: str | Path) -> "Video":
        """Open a video directory, checking it has a script and its series has a style.

        Args:
            path: The video directory (``demos/<series>/<slug>``).

        Returns:
            The video.

        Raises:
            FileNotFoundError: If ``script.yaml`` or the series' ``series.yaml`` is missing.
        """
        video = cls(Path(path).resolve())
        for required in (video.script, video.series_file):
            if not required.is_file():
                raise FileNotFoundError(f"Missing {required}")
        return video

    @property
    def slug(self) -> str:
        """The video's slug: its directory name."""
        return self.dir.name

    @property
    def series(self) -> str:
        """The series name: the name of the directory holding the video."""
        return self.dir.parent.name

    @property
    def series_file(self) -> Path:
        """``series.yaml`` of the video's series."""
        return self.dir.parent / "series.yaml"

    @property
    def style_name(self) -> str:
        """The style pack the whole series uses, read from ``series.yaml``.

        Raises:
            KeyError: If ``series.yaml`` has no ``style`` key.
        """
        return yaml.safe_load(self.series_file.read_text())["style"]

    @property
    def project(self) -> Path:
        """The user's project root."""
        return find_project_root(self.dir)

    @property
    def script(self) -> Path:
        """The narrated script."""
        return self.dir / "script.yaml"

    @property
    def audio_dir(self) -> Path:
        """Narration audio and word timings."""
        return self.dir / "audio"

    @property
    def narration_wav(self) -> Path:
        """The narration as delivered by TTS, converted to WAV."""
        return self.audio_dir / "narration.wav"

    @property
    def narration_mp3(self) -> Path:
        """A compact copy of the narration, sent for transcription."""
        return self.audio_dir / "narration.mp3"

    @property
    def words(self) -> Path:
        """Whisper word timestamps: ``{"duration": s, "words": [{word, start, end}]}``."""
        return self.audio_dir / "words.json"

    @property
    def voice_report(self) -> Path:
        """Result of ``voice.py``, tied to the spoken words and the voice it was made from."""
        return self.audio_dir / "voice.json"

    @property
    def plan_dir(self) -> Path:
        """The layout plan and the events."""
        return self.dir / "plan"

    @property
    def layout(self) -> Path:
        """The layout plan: every object on screen with its geometry and style."""
        return self.plan_dir / "layout.json"

    @property
    def events_source(self) -> Path:
        """The events as written: actions bound to anchor phrases."""
        return self.plan_dir / "events.yaml"

    @property
    def events(self) -> Path:
        """The events with anchors resolved to seconds and beats (written by plan_check)."""
        return self.plan_dir / "events.json"

    @property
    def custom(self) -> Path:
        """Optional module of video-specific components (``custom:<name>`` in the layout)."""
        return self.dir / "custom.py"

    @property
    def out(self) -> Path:
        """Generated outputs: reports, beat clips, the stitched video, review frames."""
        return self.dir / "out"

    @property
    def lint_report(self) -> Path:
        """Result of ``lint_script.py``."""
        return self.out / "lint.json"

    @property
    def plan_report(self) -> Path:
        """Result of ``plan_check.py``."""
        return self.out / "plan_check.json"

    @property
    def probe_cache(self) -> Path:
        """Geometry samples of each window, by window digest (``plan_check.py``)."""
        return self.out / "probe"

    @property
    def beats_dir(self) -> Path:
        """One clip per beat, rendered in parallel."""
        return self.out / "beats"

    @property
    def rendered(self) -> Path:
        """The stitched video with the narration."""
        return self.out / "video.mp4"

    @property
    def render_report(self) -> Path:
        """Result of ``check_render.py``."""
        return self.out / "render_check.json"

    @property
    def review_dir(self) -> Path:
        """Frames and contact sheets for the frame review."""
        return self.out / "review"

    @property
    def review_record(self) -> Path:
        """The recorded frame review that gates delivery."""
        return self.out / "review.json"

    @property
    def delivery(self) -> Path:
        """``<project>/output_videos/<series>/<slug>.mp4``."""
        return self.project / "output_videos" / self.series / f"{self.slug}.mp4"
