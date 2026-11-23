"""The narrated script (``script.yaml``) and its narrative fields.

A video is one central question (Q0) answered by a chain of units. Each unit is
question → work → turn → cash-out → link, and the turn is a wall then a revelation, an
intuition then its refutation, or a plain build. Every beat says which role it plays, so the
lint can check the chain (``docs/research/narrative-pattern.md`` §7 is the evidence).
"""

from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROLES = ("hook", "question", "setup", "dig", "attempt", "wall", "revelation", "answer",
         "consolidate", "bridge", "aside", "payoff")
WALL_SUBTYPES = ("fail", "contra", "cost", "mystery", "gap")
CONSOLIDATE_SUBTYPES = ("name", "formal", "gen", "test", "scale", "recap")
LINKS = ("causal", "return", "jump")
CONTRACT_KEYS = ("starting_point", "central_question", "initial_intuition", "anchor_example",
                 "ending_insight")
MACRO_UNIT = "u0"


@dataclass(frozen=True)
class ScriptBeat:
    """One beat of the script.

    Attributes:
        id: Unique beat id.
        role: Its narrative role (one of ``ROLES``).
        sub: Wall or consolidation subtype, when the role has one.
        unit: The unit it belongs to (``u0`` is the macro arc).
        parent: The unit's parent unit (given on the unit's first beat).
        obstruction: For walls: what blocks progress, in at most 15 words.
        against: For walls: the attempt or revelation beat the wall blocks.
        resolves: For revelations and answers: the wall, attempt or question they resolve.
        link: For revelations and answers: how the next question follows (causal, return,
            jump).
        climax: Whether this is the one revelation or answer that resolves Q0.
        say: Spoken text (no LaTeX, numbers as spoken or as digits).
        show: What the picture does, in words; the storyboard turns it into a layout plan.
    """

    id: str
    role: str
    sub: str | None
    unit: str
    parent: str | None
    obstruction: str | None
    against: str | None
    resolves: str | None
    link: str | None
    climax: bool
    say: str
    show: str


@dataclass(frozen=True)
class Script:
    """A parsed script: title, viewer contract and beats in order."""

    title: str
    contract: dict[str, str]
    beats: tuple[ScriptBeat, ...] = field(default_factory=tuple)

    def beat(self, beat_id: str) -> ScriptBeat:
        """Look up a beat by id.

        Args:
            beat_id: The beat id.

        Returns:
            The beat.

        Raises:
            KeyError: If no beat has that id.
        """
        for b in self.beats:
            if b.id == beat_id:
                return b
        raise KeyError(f"No beat {beat_id!r}")

    def narration(self) -> str:
        """The whole narration: every beat's ``say`` text joined with single spaces.

        Returns:
            The text sent to TTS.
        """
        return " ".join(" ".join(b.say.split()) for b in self.beats)


def load_script(path: Path) -> Script:
    """Read and structurally validate ``script.yaml``.

    Structure only: required keys, known roles and subtypes, unique ids, references to
    existing beats. Whether the chain makes a good video is the lint's job.

    Args:
        path: The script file.

    Returns:
        The script.

    Raises:
        ValueError: Listing every structural problem found.
    """
    data = yaml.safe_load(Path(path).read_text())
    problems: list[str] = []
    contract = data.get("viewer_contract") or {}
    problems += [f"viewer_contract.{k} is missing" for k in CONTRACT_KEYS if not contract.get(k)]
    beats: list[ScriptBeat] = []
    for raw in data.get("beats") or []:
        bid = raw.get("id", "?")
        role = raw.get("narrative_role")
        sub = raw.get("role_sub")
        if role not in ROLES:
            problems.append(f"{bid}: narrative_role {role!r} is not one of {ROLES}")
        if role == "wall" and sub not in WALL_SUBTYPES:
            problems.append(f"{bid}: a wall needs role_sub in {WALL_SUBTYPES}")
        if role == "consolidate" and sub not in CONSOLIDATE_SUBTYPES:
            problems.append(f"{bid}: a consolidate beat needs role_sub in {CONSOLIDATE_SUBTYPES}")
        if role in ("revelation", "answer") and raw.get("link") not in LINKS:
            problems.append(f"{bid}: a {role} needs link in {LINKS}")
        for key in ("unit", "say", "show"):
            if not raw.get(key):
                problems.append(f"{bid}: {key} is missing")
        beats.append(ScriptBeat(
            id=bid, role=role, sub=sub, unit=raw.get("unit", ""), parent=raw.get("parent"),
            obstruction=raw.get("obstruction"), against=raw.get("against"),
            resolves=raw.get("resolves"), link=raw.get("link"), climax=bool(raw.get("climax")),
            say=" ".join(str(raw.get("say", "")).split()), show=" ".join(str(raw.get("show", "")).split()),
        ))
    ids = [b.id for b in beats]
    problems += [f"beat id {i!r} is used twice" for i in sorted({i for i in ids if ids.count(i) > 1})]
    known = set(ids)
    for b in beats:
        for key in ("against", "resolves"):
            ref = getattr(b, key)
            if ref is not None and ref not in known:
                problems.append(f"{b.id}: {key} points to unknown beat {ref!r}")
    if not beats:
        problems.append("the script has no beats")
    if problems:
        raise ValueError("script.yaml is invalid:\n  " + "\n  ".join(problems))
    return Script(title=data.get("title", ""), contract=dict(contract), beats=tuple(beats))
