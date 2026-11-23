"""Narration timing: Whisper words, beat boundaries, and anchor phrases resolved to seconds.

Every visual change is bound to the phrase that describes it (an event's ``anchor``). Anchors
are matched against the Whisper transcript. Numbers match whether they are written in words
or digits: "one hundred forty" and "140" are the same token on both sides, because Whisper
writes some spoken numbers as digits and others as words.

Beats are located by aligning each beat's ``say`` text to the transcript; a beat ends in the
pause before the next beat's first word, which is where the parallel renderer cuts. The same
alignment finds stretches of the script the transcript never heard, so words Whisper dropped
are caught at voicing time instead of silently shifting beats and anchors.
"""

import json
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from itertools import pairwise
from pathlib import Path

UNITS = {w: i for i, w in enumerate((
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve",
    "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"))}
TENS = {w: 10 * (i + 2) for i, w in enumerate(
    ("twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"))}
SCALES = {"hundred": 100, "thousand": 1000, "million": 1_000_000}


@dataclass(frozen=True)
class Word:
    """One transcribed word and when it is spoken."""

    text: str
    start: float
    end: float


@dataclass(frozen=True)
class Unit:
    """A matching token and the transcript words it covers (a number may span several).

    Attributes:
        token: The normalized token; number words become digits.
        first: Index of its first word.
        last: Index of its last word.
    """

    token: str
    first: int
    last: int


@dataclass(frozen=True)
class Transcript:
    """The narration's words and its exact audio duration (seconds)."""

    words: tuple[Word, ...]
    duration: float

    @classmethod
    def load(cls, path: Path) -> "Transcript":
        """Read ``audio/words.json``.

        Args:
            path: The words file written by ``voice.py``.

        Returns:
            The transcript.

        Raises:
            FileNotFoundError: If the narration has not been voiced yet.
        """
        data = json.loads(Path(path).read_text())
        words = tuple(Word(w["word"], float(w["start"]), float(w["end"])) for w in data["words"])
        return cls(words, float(data["duration"]))

    def units(self) -> list[Unit]:
        """The transcript as matching units: one per word, number-word runs merged.

        Returns:
            Units in order, each knowing the word indices it covers.
        """
        tokens: list[tuple[str, int]] = []
        for index, word in enumerate(self.words):
            tokens.extend((t, index) for t in tokenize(word.text))
        return numberize(tokens)


@dataclass(frozen=True)
class Beat:
    """A beat's place in the narration.

    Attributes:
        id: The beat id from ``script.yaml``.
        start: Where the beat's clip starts (s); 0 for the first beat.
        end: Where it ends (s); the audio duration for the last beat.
        first_word: Index of the beat's first transcript word.
        last_word: Index of its last transcript word.
    """

    id: str
    start: float
    end: float
    first_word: int
    last_word: int


def normalize(token: str) -> str:
    """Normalize a word for matching: lowercase, letters, digits and apostrophes only.

    Args:
        token: A word as written or transcribed.

    Returns:
        The normalized token ("" for pure punctuation).
    """
    return re.sub(r"[^a-z0-9']", "", token.lower().replace("’", "'"))


def tokenize(text: str) -> list[str]:
    """Split text into normalized words, dropping empty ones (for counting words).

    Hyphenated and slashed compounds split into their parts, as Whisper writes them.

    Args:
        text: Any narration text.

    Returns:
        The words.
    """
    parts = re.split(r"[\s\-–—/]+", text)
    return [t for t in (normalize(p) for p in parts) if t]


def number_value(token: str) -> int | None:
    """The value of a number word (units and tens only).

    Args:
        token: A normalized token.

    Returns:
        Its value, or None if it is not a units or tens word.
    """
    return UNITS.get(token, TENS.get(token))


def numberize(tokens: list[tuple[str, int]]) -> list[Unit]:
    """Merge runs of number words into one digit token, keeping which positions each covers.

    "one hundred forty", "a hundred and forty" and "140" all become ``140``; "eighty nine"
    becomes ``89``. A run breaks where a new number must begin ("five six" stays 5 and 6).

    Args:
        tokens: ``(token, position)`` pairs, positions in order.

    Returns:
        Units: plain tokens pass through; number runs become one digit unit.
    """
    units: list[Unit] = []
    total, current, start, end = 0, 0, -1, -1

    def flush() -> None:
        """Emit the number being built, if any, and reset the run."""
        nonlocal total, current, start, end
        if start >= 0:
            units.append(Unit(str(total + current), start, end))
        total, current, start, end = 0, 0, -1, -1

    for i, (token, position) in enumerate(tokens):
        following = tokens[i + 1][0] if i + 1 < len(tokens) else ""
        value = number_value(token)
        if value is not None:
            if start >= 0 and ((value < 10 and current % 10) or (value >= 10 and current % 100)):
                flush()
            current += value
        elif token in SCALES and (start >= 0 or token == "hundred"):
            if SCALES[token] == 100:
                current = max(current, 1) * 100
            else:
                total += max(current, 1) * SCALES[token]
                current = 0
        elif token == "a" and following in SCALES:
            flush()
            current = 1
        elif token == "and" and start >= 0 and current % 100 == 0 and number_value(following) is not None:
            pass
        else:
            flush()
            units.append(Unit(token, position, position))
            continue
        start = position if start < 0 else start
        end = position
    flush()
    return units


def matching_tokens(text: str) -> list[str]:
    """Text as matching tokens: normalized words with number-word runs as digits.

    Args:
        text: Script or anchor text.

    Returns:
        The tokens.
    """
    return [u.token for u in numberize([(t, i) for i, t in enumerate(tokenize(text))])]


def align(beat_texts: list[tuple[str, str]], transcript: Transcript) -> tuple[list[int], dict[int, int], list[Unit]]:
    """Align the script's tokens to the transcript's units.

    Args:
        beat_texts: ``(beat id, say text)`` in script order.
        transcript: The narration's words.

    Returns:
        The beat index of every script token, a map from script token index to the unit it
        matched, and the transcript's units.
    """
    script_tokens: list[str] = []
    owner: list[int] = []
    for index, (_, text) in enumerate(beat_texts):
        tokens = matching_tokens(text)
        script_tokens.extend(tokens)
        owner.extend([index] * len(tokens))
    units = transcript.units()
    matcher = SequenceMatcher(None, script_tokens, [u.token for u in units], autojunk=False)
    matched = {block.a + k: block.b + k for block in matcher.get_matching_blocks() for k in range(block.size)}
    return owner, matched, units


def unheard_phrases(beat_texts: list[tuple[str, str]], transcript: Transcript, min_run: int) -> list[tuple[str, str]]:
    """Stretches of the script the transcript did not hear: the signature of dropped speech.

    Isolated misses (a number written differently, a split compound) are normal; a run of
    ``min_run`` or more consecutive unheard words is not.

    Args:
        beat_texts: ``(beat id, say text)`` in script order.
        transcript: The narration's words.
        min_run: Shortest run of consecutive unheard tokens to report.

    Returns:
        ``(beat id, the unheard words)`` for every such run.
    """
    owner, matched, _ = align(beat_texts, transcript)
    tokens = [t for _, text in beat_texts for t in matching_tokens(text)]
    runs, run = [], []
    for i, token in enumerate([*tokens, None]):
        if token is not None and i not in matched and (not run or owner[run[-1]] == owner[i]):
            run.append(i)
            continue
        if len(run) >= min_run:
            runs.append((beat_texts[owner[run[0]]][0], " ".join(tokens[k] for k in run)))
        run = [i] if token is not None and i not in matched else []
    return runs


def locate_beats(beat_texts: list[tuple[str, str]], transcript: Transcript) -> list[Beat]:
    """Find where each beat is spoken by aligning the script to the transcript.

    A beat owns every transcript word after the previous beat's last matched word up to its
    own last matched word. Clip boundaries fall in the middle of the pause between two beats.

    Args:
        beat_texts: ``(beat id, say text)`` in script order.
        transcript: The narration's words.

    Returns:
        One ``Beat`` per script beat, contiguous from 0 to the audio duration.

    Raises:
        ValueError: If a beat's words cannot be found in the transcript.
    """
    owner, matched, units = align(beat_texts, transcript)
    last_heard: dict[int, int] = {}
    for script_index, unit_index in matched.items():
        last_heard[owner[script_index]] = max(last_heard.get(owner[script_index], -1), units[unit_index].last)
    beats: list[Beat] = []
    first = 0
    last_word = len(transcript.words) - 1
    for index, (beat_id, _) in enumerate(beat_texts):
        if index not in last_heard or last_heard[index] < first:
            raise ValueError(f"Beat {beat_id!r} is not found in the transcript; re-run voice.py")
        last = last_word if index == len(beat_texts) - 1 else last_heard[index]
        beats.append(Beat(beat_id, 0.0, 0.0, first, last))
        first = last + 1
    words = transcript.words
    cuts = [0.0]
    for left, right in pairwise(beats):
        cuts.append(round((words[left.last_word].end + words[right.first_word].start) / 2, 3))
    cuts.append(transcript.duration)
    return [Beat(b.id, cuts[i], cuts[i + 1], b.first_word, b.last_word) for i, b in enumerate(beats)]


def resolve_anchor(anchor: str, transcript: Transcript, cursor: int) -> tuple[int, int]:
    """Find an anchor phrase in the transcript at or after a word index.

    Anchors are matched in event order, so the same phrase spoken twice resolves to the
    occurrence after the previous event's anchor. Numbers match in words or digits.

    Args:
        anchor: The phrase.
        transcript: The narration's words.
        cursor: The first word index to search from.

    Returns:
        ``(first word index, last word index)`` of the match.

    Raises:
        ValueError: If the phrase does not occur at or after ``cursor``; the message shows
            the transcript there so the anchor can be corrected.
    """
    want = matching_tokens(anchor)
    if not want:
        raise ValueError(f"Empty anchor {anchor!r}")
    units = [u for u in transcript.units() if u.first >= cursor]
    tokens = [u.token for u in units]
    for i in range(len(tokens) - len(want) + 1):
        if tokens[i:i + len(want)] == want:
            return units[i].first, units[i + len(want) - 1].last
    context = " ".join(w.text for w in transcript.words[cursor:cursor + 40])
    raise ValueError(f"Anchor {anchor!r} not found after word {cursor}. Transcript from there: {context!r}")
