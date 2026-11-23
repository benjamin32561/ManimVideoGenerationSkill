"""Style packs: everything that differs between a 3Blue1Brown video and a Welch Labs video.

A pack lives in ``styles/<name>/``:

* ``style.yaml``     voice, speaker profile, narrative parameters, canvas, colours, fonts,
                     text policy, motion numbers, emphasis vocabulary, rule overrides
* ``components.py``  the style's reusable objects, used as ``component`` layout objects
* ``STYLE.md``       how a video in the style flows and looks, and why

The series chooses the pack (``series.yaml`` → ``style``); every video of a series uses it.
"""

import importlib.util
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

import yaml

from explain.paths import SKILL_ROOT

STYLES_DIR = SKILL_ROOT / "styles"
FONT_SUFFIXES = (".otf", ".ttf", ".ttc")


@dataclass(frozen=True)
class Voice:
    """How the narration is spoken.

    Attributes:
        model: OpenRouter TTS model id.
        voice: The model's voice name.
        instructions: The delivery instruction sent with every request (pace, register).
        sample_rate: Sample rate of the raw PCM the model returns.
        max_chars: The longest text sent in one request; longer scripts are split at unit
            boundaries.
    """

    model: str
    voice: str
    instructions: str
    sample_rate: int
    max_chars: int


@dataclass(frozen=True)
class Canvas:
    """The frame: pixel size, frame rate and background colour."""

    width: int
    height: int
    fps: int
    background: str


@dataclass(frozen=True)
class TextPolicy:
    """Rules for on-screen text.

    Attributes:
        families: Font name → (family, directory with its files). ``default`` is used unless a
            text object names another (Welch sets example sentences in a serif italic).
        roles: Named sizes in px (CSS font-size at 1080p), e.g. ``label: 34``.
        min_px: Smallest size any text or math may have.
        max_words: Word budget per text, by role; texts without a role use ``default``.
        backstroke_px: Width of the black stroke drawn behind text marked ``backstroke``.
        uppercase_roles: Roles whose content must be written in capitals (Welch labels).
    """

    families: dict[str, tuple[str, Path]]
    roles: dict[str, float]
    min_px: float
    max_words: dict[str, int]
    backstroke_px: float
    uppercase_roles: tuple[str, ...]


@dataclass(frozen=True)
class Motion:
    """Timing numbers for the action vocabulary (seconds unless noted).

    Attributes:
        start_offset: Delay of an event's first change after its anchor's first word.
        sync_window: Allowed [earliest, latest] first visible change after the anchor, for
            the render check.
        write: [min, max] run time of a write-on.
        write_mode: ``glyph`` (stroke then fill, 3b1b) or ``letters`` (letter by letter,
            Welch caps labels).
        letters_per_s: Typing rate in ``letters`` mode.
        draw: [min, max] run time of a stroke draw-on.
        grow: [min, max] run time of one object growing in a staggered group.
        fade_in: Longest fade-in.
        fade_out: Longest fade-out (exits are shorter than entrances).
        morph: Run time of a matched-part morph.
        copy: Run time of a copy flying into its target.
        dim: Run time of a dim or restore.
        change: [min, max] run time of a geometry change.
        flash_peak: Peak opacity of a flash highlight.
        flash_pad_px: Padding of a flash highlight around its target.
    """

    start_offset: float
    sync_window: tuple[float, float]
    write: tuple[float, float]
    write_mode: str
    letters_per_s: float
    draw: tuple[float, float]
    grow: tuple[float, float]
    fade_in: float
    fade_out: float
    morph: float
    copy: float
    dim: float
    change: tuple[float, float]
    flash_peak: float
    flash_pad_px: float


@dataclass(frozen=True)
class Style:
    """A loaded style pack.

    Attributes:
        name: The pack's directory name.
        title: Human-readable name.
        dir: The pack's directory.
        voice: Narration voice.
        speaker: Speaker-profile targets: metric → [min, max] (wpm, pauses, sentences,
            questions, pronouns, contractions); the script lint warns outside them.
        narrative: Narrative-grammar parameters (turn budget, intro length, climax range...).
        canvas: Frame size, rate and background.
        colors: Palette token → hex colour.
        text: On-screen text policy.
        motion: Motion timing numbers.
        banned_actions: Event actions this style never uses.
        rules: Style switches for the script lint (exact numbers, prose on plots...).
    """

    name: str
    title: str
    dir: Path
    voice: Voice
    speaker: dict[str, tuple[float, float]]
    narrative: dict
    canvas: Canvas
    colors: dict[str, str]
    text: TextPolicy
    motion: Motion
    banned_actions: tuple[str, ...]
    rules: dict

    def color(self, token: str) -> str:
        """Resolve a palette token.

        Args:
            token: A key of the palette, e.g. ``yellow``.

        Returns:
            The hex colour.

        Raises:
            KeyError: If the palette has no such token.
        """
        if token not in self.colors:
            raise KeyError(f"Style {self.name!r} has no colour {token!r}; palette: {sorted(self.colors)}")
        return self.colors[token]

    def components(self) -> ModuleType:
        """Import the pack's ``components.py``.

        Returns:
            The module; its public functions are the style's components.
        """
        return import_file(self.dir / "components.py", f"explain_style_{self.name}")


def import_file(path: Path, name: str) -> ModuleType:
    """Import a Python file as a module without putting its directory on ``sys.path``.

    Args:
        path: The ``.py`` file.
        name: The module name to register it under.

    Returns:
        The executed module.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not path.is_file():
        raise FileNotFoundError(f"Missing {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pair(value: list) -> tuple[float, float]:
    """Read a ``[min, max]`` pair from YAML.

    Args:
        value: A two-element list.

    Returns:
        The pair as floats.

    Raises:
        ValueError: If the list does not have exactly two numbers with min <= max.
    """
    low, high = (float(v) for v in value)
    if low > high:
        raise ValueError(f"Range {value} has min > max")
    return low, high


def check_fonts(text: TextPolicy) -> None:
    """Fail unless every font family's files are installed where the style says.

    A missing font is a broken install, not something to paper over with a fallback font.

    Args:
        text: The style's text policy.

    Raises:
        FileNotFoundError: If a font directory is missing or holds no font files.
    """
    for family, font_dir in text.families.values():
        files = [p for p in font_dir.glob("*") if p.suffix.lower() in FONT_SUFFIXES] if font_dir.is_dir() else []
        if not files:
            raise FileNotFoundError(f"Font {family!r} is not installed in {font_dir}. Install it there "
                                    f"(see the style's STYLE.md) before rendering.")


def load_style(name: str) -> Style:
    """Load and validate a style pack.

    Args:
        name: The pack's directory name under ``styles/``.

    Returns:
        The style.

    Raises:
        FileNotFoundError: If the pack or its fonts are missing.
        KeyError: If ``style.yaml`` lacks a required key.
        ValueError: If a range is malformed.
    """
    pack = STYLES_DIR / name
    data = yaml.safe_load((pack / "style.yaml").read_text())
    v, t, mo = data["voice"], data["text"], data["motion"]
    text = TextPolicy(
        families={name: (f["family"], Path(f["dir"]).expanduser()) for name, f in t["families"].items()},
        roles={k: float(px) for k, px in t["roles"].items()},
        min_px=float(t["min_px"]),
        max_words={k: int(n) for k, n in t["max_words"].items()},
        backstroke_px=float(t["backstroke_px"]),
        uppercase_roles=tuple(t.get("uppercase_roles", ())),
    )
    check_fonts(text)
    return Style(
        name=name,
        title=data["title"],
        dir=pack,
        voice=Voice(model=v["model"], voice=v["voice"], instructions=" ".join(v["instructions"].split()),
                    sample_rate=int(v["sample_rate"]), max_chars=int(v["max_chars"])),
        speaker={k: pair(r) for k, r in data["speaker"].items()},
        narrative=data["narrative"],
        canvas=Canvas(**data["canvas"]),
        colors=dict(data["colors"]),
        text=text,
        motion=Motion(
            start_offset=float(mo["start_offset"]),
            sync_window=pair(mo["sync_window"]),
            write=pair(mo["write"]),
            write_mode=mo["write_mode"],
            letters_per_s=float(mo["letters_per_s"]),
            draw=pair(mo["draw"]),
            grow=pair(mo["grow"]),
            fade_in=float(mo["fade_in"]),
            fade_out=float(mo["fade_out"]),
            morph=float(mo["morph"]),
            copy=float(mo["copy"]),
            dim=float(mo["dim"]),
            change=pair(mo["change"]),
            flash_peak=float(mo["flash_peak"]),
            flash_pad_px=float(mo["flash_pad_px"]),
        ),
        banned_actions=tuple(data["emphasis"]["banned_actions"]),
        rules=data["rules"],
    )
