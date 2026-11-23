"""The layout plan and the timed events: what is on screen, where, and when it changes.

``plan/layout.json`` places every object in the canvas' pixel space (origin top-left, y down)::

    {"objects": {"<id>": {"type": "text", ...}, ...},
     "groups":  {"<name>": ["<id>", ...]},
     "paths":   {"<name>": {"<object id>": [[x, y], ...]}}}

``plan/events.yaml`` binds actions to the phrases that describe them::

    events:
      - id: e01
        anchor: "picture a cell membrane"
        do:
          - {action: draw, targets: [membrane]}

``plan_check.py`` resolves anchors to seconds and writes ``plan/events.json``; the renderer
reads only that file. Every object enters through an entrance action; nothing is placed
freehand by code.
"""

import hashlib
import json
from dataclasses import dataclass
from importlib.metadata import version
from pathlib import Path

import yaml

from explain.paths import SKILL_ROOT, Video
from explain.report import digest_files
from explain.script import Script
from explain.styles import Style, Voice
from explain.timing import Beat, Transcript, locate_beats, resolve_anchor

OBJECT_FIELDS: dict[str, tuple[str, ...]] = {
    "text": ("content", "x", "y", "size", "color"),
    "math": ("x", "y", "size", "color"),
    "circle": ("cx", "cy", "r", "fill"),
    "rect": ("x0", "y0", "x1", "y1"),
    "line": ("points", "stroke", "stroke_width"),
    "arrow": ("points", "stroke", "stroke_width"),
    "polygon": ("points", "fill"),
    "symbol": ("glyph", "x", "y", "size", "color"),
    "box": ("around", "padding", "stroke", "stroke_width"),
    "brace": ("around", "side", "color"),
    "component": ("name",),
}
TEXT_TYPES = ("text", "math", "symbol")
GLYPHS = ("+", "−", "×", "=")
ENTRANCES = ("draw", "write", "grow", "fade_in")
ACTION_FIELDS: dict[str, tuple[str, ...]] = {
    "draw": ("targets",),
    "write": ("targets",),
    "grow": ("targets",),
    "fade_in": ("targets",),
    "fade_out": ("targets",),
    "move": ("targets",),
    "change": ("targets", "to"),
    "recolor": ("targets", "color"),
    "dim": ("targets", "opacity"),
    "restore": ("targets",),
    "flash": ("targets", "color"),
    "copy_to": ("source", "target"),
    "morph": ("source", "target"),
}
GROW_FROM = ("center", "tail", "bottom", "top", "left", "right")
COMPATIBLE_PAIR = {"recolor", "dim"}


@dataclass(frozen=True)
class Layout:
    """A parsed layout plan.

    Attributes:
        objects: Object id → its spec (``type`` plus the type's fields).
        groups: Group name → member ids (objects, parts or other groups).
        paths: Path name → object id → waypoints in px.
        parts: Math part id → the id of the math object that owns it.
    """

    objects: dict[str, dict]
    groups: dict[str, list[str]]
    paths: dict[str, dict[str, list[list[float]]]]
    parts: dict[str, str]

    def leaves(self, ids: list[str]) -> list[str]:
        """Expand ids into the leaf ids that appear on screen on their own.

        Groups expand to their members; a math object with named parts expands to its parts;
        everything else is a leaf.

        Args:
            ids: Object ids, part ids or group names.

        Returns:
            Leaf ids in order, without duplicates.

        Raises:
            KeyError: If an id is neither an object, a part nor a group.
        """
        out: list[str] = []
        for oid in ids:
            if oid in self.groups:
                expanded = self.leaves(self.groups[oid])
            elif oid in self.objects and self.objects[oid].get("parts"):
                expanded = [p["id"] for p in self.objects[oid]["parts"] if p.get("id")]
            elif oid in self.objects or oid in self.parts:
                expanded = [oid]
            else:
                raise KeyError(f"Unknown object, part or group {oid!r}")
            out.extend(e for e in expanded if e not in out)
        return out

    def is_text(self, leaf: str) -> bool:
        """Whether a leaf is text or math (parts of a math object are math).

        Args:
            leaf: A leaf id.

        Returns:
            True for text and math leaves.
        """
        return leaf in self.parts or self.objects[leaf]["type"] in TEXT_TYPES or bool(
            self.objects[leaf].get("text_like"))


def load_layout(path: Path) -> Layout:
    """Read and validate ``plan/layout.json``.

    Args:
        path: The layout file.

    Returns:
        The layout.

    Raises:
        ValueError: Listing every problem: unknown types, missing fields, duplicate part ids,
            references to unknown objects.
    """
    data = json.loads(Path(path).read_text())
    objects = data.get("objects") or {}
    problems: list[str] = []
    parts: dict[str, str] = {}
    for oid, spec in objects.items():
        kind = spec.get("type")
        if kind not in OBJECT_FIELDS:
            problems.append(f"{oid}: unknown type {kind!r}; known: {sorted(OBJECT_FIELDS)}")
            continue
        problems += [f"{oid}: {kind} needs {f!r}" for f in OBJECT_FIELDS[kind] if f not in spec]
        if kind == "symbol" and spec.get("glyph") not in GLYPHS:
            problems.append(f"{oid}: symbol glyph must be one of {GLYPHS}")
        if kind == "math" and not (spec.get("tex") or spec.get("parts")):
            problems.append(f"{oid}: math needs 'tex' or 'parts'")
        for part in spec.get("parts") or []:
            pid = part.get("id")
            if pid is None:
                continue
            if pid in parts or pid in objects:
                problems.append(f"{oid}: part id {pid!r} is already used")
            parts[pid] = oid
        if kind in ("box", "brace") and spec.get("around") not in objects and spec.get("around") not in parts:
            problems.append(f"{oid}: 'around' points to unknown object {spec.get('around')!r}")
    groups = data.get("groups") or {}
    known = set(objects) | set(parts) | set(groups)
    for name, members in groups.items():
        problems += [f"group {name}: unknown member {m!r}" for m in members if m not in known]
    paths = data.get("paths") or {}
    for name, per_object in paths.items():
        problems += [f"path {name}: unknown object {o!r}" for o in per_object if o not in objects]
    if problems:
        raise ValueError("layout.json is invalid:\n  " + "\n  ".join(problems))
    return Layout(objects=objects, groups=groups, paths=paths, parts=parts)


@dataclass(frozen=True)
class Event:
    """One resolved event: actions that start on an anchor phrase and end with it.

    Attributes:
        id: Event id.
        anchor: The phrase, as written.
        start: First anchor word's start (s).
        end: Last anchor word's end (s).
        beat: The beat whose clip contains ``start``.
        actions: The actions, as written.
    """

    id: str
    anchor: str
    start: float
    end: float
    beat: str
    actions: tuple[dict, ...]


@dataclass(frozen=True)
class Timeline:
    """The resolved events and beats of a video (``plan/events.json``)."""

    duration: float
    beats: tuple[Beat, ...]
    events: tuple[Event, ...]

    @classmethod
    def load(cls, path: Path) -> "Timeline":
        """Read ``plan/events.json``.

        Args:
            path: The resolved events file.

        Returns:
            The timeline.
        """
        data = json.loads(Path(path).read_text())
        beats = tuple(Beat(**b) for b in data["beats"])
        events = tuple(Event(e["id"], e["anchor"], e["start"], e["end"], e["beat"], tuple(e["do"]))
                       for e in data["events"])
        return cls(float(data["duration"]), beats, events)

    def save(self, path: Path) -> None:
        """Write ``plan/events.json``.

        Args:
            path: Destination.
        """
        Path(path).write_text(json.dumps({
            "duration": self.duration,
            "beats": [vars(b) for b in self.beats],
            "events": [{"id": e.id, "anchor": e.anchor, "start": e.start, "end": e.end,
                        "span": round(e.end - e.start, 3), "beat": e.beat, "do": list(e.actions)}
                       for e in self.events],
        }, indent=1, ensure_ascii=False) + "\n")


def validate_events(raw_events: list[dict], layout: Layout, style: Style) -> list[str]:
    """Check every event's actions against the vocabulary, the layout and object lifecycles.

    Lifecycle: a leaf enters once (entrance action, ``copy_to`` target or ``morph`` target)
    before anything else may act on it, and leaves through ``fade_out`` or as a ``morph``
    source; it may re-enter after leaving. Within one event a leaf is animated by one action
    only (a recolor followed by a dim is the one allowed pair), because two animations of
    the same object in one play fight over it.

    Args:
        raw_events: Events as written in ``events.yaml``.
        layout: The layout plan.
        style: The series' style (for banned actions and colour tokens).

    Returns:
        Problems found (empty when the events are valid).
    """
    problems: list[str] = []
    on_screen: set[str] = set()
    ids = [e.get("id") for e in raw_events]
    problems += [f"event id {i!r} is used twice" for i in sorted({i for i in ids if ids.count(i) > 1})]
    for event in raw_events:
        eid = event.get("id", "?")
        if not event.get("anchor"):
            problems.append(f"{eid}: anchor is missing")
        if not event.get("do"):
            problems.append(f"{eid}: has no actions")
        touched: dict[str, str] = {}
        for action in event.get("do") or []:
            kind = action.get("action")
            where = f"{eid} {kind}"
            if kind not in ACTION_FIELDS:
                problems.append(f"{where}: unknown action; known: {sorted(ACTION_FIELDS)}")
                continue
            if kind in style.banned_actions:
                problems.append(f"{where}: the {style.name} style bans this action")
            problems += [f"{where}: needs {f!r}" for f in ACTION_FIELDS[kind] if f not in action]
            if "color" in action and action["color"] not in style.colors:
                problems.append(f"{where}: unknown colour {action['color']!r}")
            if kind == "grow" and action.get("from", "center") not in GROW_FROM:
                problems.append(f"{where}: 'from' must be one of {GROW_FROM}")
            if kind == "move" and ("to" in action) == ("along" in action):
                problems.append(f"{where}: give exactly one of 'to' or 'along'")
            if kind == "move" and "along" in action and action["along"] not in layout.paths:
                problems.append(f"{where}: unknown path {action['along']!r}")
            try:
                if kind in ("copy_to", "morph"):
                    sources, targets = layout.leaves([action["source"]]), layout.leaves([action["target"]])
                else:
                    sources, targets = [], layout.leaves(action.get("targets", []))
            except KeyError as err:
                problems.append(f"{where}: {err.args[0]}")
                continue
            if kind == "grow" and action.get("from") == "tail":
                problems += [f"{where}: {leaf} has no 'points' to grow from" for leaf in targets
                             if "points" not in layout.objects.get(leaf, {})]
            if kind in ENTRANCES or kind in ("copy_to", "morph"):
                entering = targets
                problems += [f"{where}: {leaf} is already on screen" for leaf in entering if leaf in on_screen]
            else:
                entering = []
            for leaf in targets + (sources if kind == "morph" else []):
                if leaf in touched and {touched[leaf], kind} != COMPATIBLE_PAIR:
                    problems.append(f"{where}: {leaf} is already animated by {touched[leaf]} in this event")
                touched[leaf] = kind
            needed = sources + ([] if entering else targets)
            problems += [f"{where}: {leaf} is not on screen yet" for leaf in needed if leaf not in on_screen]
            on_screen |= set(entering)
            if kind == "fade_out":
                on_screen -= set(targets)
            if kind == "morph":
                on_screen -= set(sources)
    return problems


def resolve_timeline(raw_events: list[dict], script: Script, transcript: Transcript) -> Timeline:
    """Resolve every event's anchor to seconds and assign it to the beat it starts in.

    Args:
        raw_events: Events as written in ``events.yaml``.
        script: The script (beats in order).
        transcript: The narration's words.

    Returns:
        The timeline, ready to save as ``plan/events.json``.

    Raises:
        ValueError: If a beat or an anchor cannot be found in the transcript.
    """
    beats = locate_beats([(b.id, b.say) for b in script.beats], transcript)
    events: list[Event] = []
    cursor = 0
    for raw in raw_events:
        first, last = resolve_anchor(raw["anchor"], transcript, cursor)
        cursor = first + 1
        start, end = transcript.words[first].start, transcript.words[last].end
        beat = next(b.id for b in beats if b.start <= start < b.end)
        events.append(Event(raw["id"], raw["anchor"], start, end, beat, tuple(raw["do"])))
    return Timeline(transcript.duration, tuple(beats), tuple(events))


def load_raw_events(path: Path) -> list[dict]:
    """Read the events as written.

    Args:
        path: ``plan/events.yaml``.

    Returns:
        The list under ``events``.
    """
    return yaml.safe_load(Path(path).read_text())["events"]


def script_digest(video: Video, style: Style) -> str:
    """Hash what the script lint judged: the script, the series file and the style.

    Args:
        video: The video.
        style: Its style pack.

    Returns:
        A hex SHA-256.
    """
    return digest_files(video.script, video.series_file, style.dir / "style.yaml")


def narration_digest(script: Script, voice: Voice) -> str:
    """Hash what the narration audio is made from: every beat's spoken words and the voice.

    ``show`` text and narrative fields are left out, so changing them does not call for a new
    voicing; changing a single spoken word or the style's voice does.

    Args:
        script: The script.
        voice: The style's voice (model, voice name, delivery instruction, sample rate, request size).

    Returns:
        A hex SHA-256.
    """
    parts = [b.say for b in script.beats]
    parts += [voice.model, voice.voice, voice.instructions, str(voice.sample_rate), str(voice.max_chars)]
    return hashlib.sha256("\n".join(parts).encode()).hexdigest()


def code_digest(video: Video, style: Style) -> str:
    """Hash what every frame depends on besides the plan itself.

    Args:
        video: The video (its ``custom.py``).
        style: Its style pack (``style.yaml`` and ``components.py``).

    Returns:
        A hex SHA-256 over the skill's runtime code (``explain/*.py``), the manimgx version, the
        style pack and the video's custom components.
    """
    return digest_files(*sorted((SKILL_ROOT / "explain").glob("*.py")), style.dir / "style.yaml",
                        style.dir / "components.py", video.custom, extra=version("manimgx"))


def plan_digest(video: Video, style: Style) -> str:
    """Hash everything a render depends on, so reports and reviews can be tied to it.

    Args:
        video: The video.
        style: Its style pack.

    Returns:
        A hex SHA-256 over the script, words, layout and events, plus ``code_digest``: a change
        to the skill's code, the style or the custom components makes every check stale.
    """
    return digest_files(video.script, video.words, video.layout, video.events_source,
                        extra=code_digest(video, style))
