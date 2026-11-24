"""The script lint: the narrative grammar (rules N1–N15) and the style's speaker profile.

A video is ``Hook Q0 Unit+ Payoff``. Each unit runs question → work → turn → cash-out →
link, the turn being a wall then a revelation, an intuition then its refutation, or a plain
build; one climax resolves Q0; the payoff calls back to the opening. The numbers come from
the series' style (``narrative`` and ``speaker`` in ``style.yaml``); the evidence is
``docs/research/narrative-pattern.md``.

Timing: before the voice exists, beat times are estimated from word counts at the style's
pace; afterwards the real times come from the transcript, and pace and pauses are checked.
"""

import re
from dataclasses import dataclass

from explain.problems import Problem
from explain.script import MACRO_UNIT, Script, ScriptBeat
from explain.styles import Style
from explain.timing import Transcript, locate_beats, matching_tokens, tokenize

WORK_ROLES = ("setup", "dig", "attempt")
TURN_ROLES = ("revelation", "answer")
QUESTION_OPENERS = ("how", "why", "what", "where", "when", "which", "who", "can", "could", "is", "are",
                    "does", "do", "did", "would", "should", "will")
TURN_MARKERS = ("but", "however", "problem", "doesn't", "can't", "cannot", "not enough", "fails", "won't",
                "isn't", "never", "wait", "breaks", "stuck", "impossible")
EVALUATIVE = ("remarkable", "beautiful", "elegant", "clever", "amazing", "stunning", "brilliant", "magical")
DIALOGUE = re.compile(r"\b(?:[A-Z][a-z]+|he|she) (?:says|said|asks|asked|replies|replied)\b|\bI'm like\b|\bI say\b")
CLARIFYING_I_SAY = re.compile(r"\b(?:when|what|as)\s+I say\b", re.IGNORECASE)
LATEX = re.compile(r"[\\^_$]")
EXACT_NUMBER = re.compile(r"\b\d+\.\d+\b|\b(?!1[89]\d\d\b|20\d\d\b)\d{4,}\b")
_NUM_WORDS = (
    r"zero|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
    r"thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|"
    r"twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|"
    r"hundred|thousand|million|billion|trillion"
)
_FRAC_WORDS = (
    r"half|halves|third|thirds|quarter|quarters|"
    r"fourth|fourths|fifth|fifths|eighth|eighths|tenth|tenths|sixteenth|sixteenths"
)
_NUM_TAIL = rf"{_NUM_WORDS}|one|point|percent|{_FRAC_WORDS}"
NON_QUANTITY = re.compile(r"\b[A-Za-z][A-Za-z0-9]*-\d+\b|\bbase[\s-]+(?:two|ten|2|10)\b", re.IGNORECASE)
NUMBER_MENTION = re.compile(
    rf"(?:\b(?!1[89]\d\d\b|20\d\d\b)\d+(?:,\d{{3}})*(?:\.\d+)?%?(?:\s*(?:percent|million|billion|thousand|hundred))?\b"
    rf"|\b(?:(?:minus|negative|plus)\s+(?:one|{_NUM_WORDS})"
    rf"|(?:{_NUM_WORDS})"
    rf"|one[\s-]+(?:and[\s-]+(?:a[\s-]+)?(?:{_FRAC_WORDS}|{_NUM_WORDS})|hundred|thousand|million|billion|trillion|percent|point|{_FRAC_WORDS})"
    rf"|(?:a|an)\s+(?:{_FRAC_WORDS}))"
    rf"(?:[\s-]+(?:and\s+)?(?:a\s+)?(?:{_NUM_TAIL}))*"
    rf"(?:\s*percent)?\b)",
    re.IGNORECASE,
)
EXACT_SPEC = re.compile(
    r"\b\d+(?:\.\d+)?\s*(?:%|percent)\b|\b\d+\.\d+\b"
    r"|\b(?!1[89]\d\d\b|20\d\d\b)\d{1,3}(?:,\d{3})+\b"
    r"|\b(?!1[89]\d\d\b|20\d\d\b)\d{3,}\b",
    re.IGNORECASE,
)
BEAT_NUMBER_RATE_MIN = 8.0
CONTRACTION = re.compile(r"\b\w+'(?:s|re|ve|ll|d|t|m)\b", re.IGNORECASE)
RUN_ON_NUMBER = re.compile(r"\b(?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred)[\s,]+"
                           r"(?:too|to|two|for|four|ate|won)\b", re.IGNORECASE)
LONG_PAUSE_S = 1.0
STOPWORDS = {"there", "their", "these", "those", "about", "would", "could", "should", "which", "where",
             "while", "every", "other", "being", "think", "thing", "things", "really", "something"}


@dataclass(frozen=True)
class Timed:
    """A beat with its place in time.

    Attributes:
        beat: The script beat.
        start: Start (s).
        end: End (s).
    """

    beat: ScriptBeat
    start: float
    end: float


def place_beats(script: Script, style: Style, transcript: Transcript | None) -> tuple[list[Timed], float]:
    """Give every beat a start and end time: real when voiced, estimated otherwise.

    Args:
        script: The script.
        style: The series' style (its pace for estimates).
        transcript: The narration's words, or None before voicing.

    Returns:
        The timed beats and the total length (s).
    """
    if transcript is not None:
        located = locate_beats([(b.id, b.say) for b in script.beats], transcript)
        return [Timed(b, loc.start, loc.end) for b, loc in zip(script.beats, located, strict=True)], transcript.duration
    words_per_s = sum(style.speaker["wpm"]) / 2 / 60
    timed, t = [], 0.0
    for b in script.beats:
        length = len(tokenize(b.say)) / words_per_s
        timed.append(Timed(b, t, t + length))
        t += length
    return timed, t


def sentences(text: str) -> list[str]:
    """Split text into sentences at ., ! and ?.

    Args:
        text: Narration.

    Returns:
        Non-empty sentences, each keeping its final mark.
    """
    return [s.strip() for s in re.findall(r"[^.!?]+[.!?]*", text) if s.strip(" .!?")]


def is_question(text: str) -> bool:
    """Whether a beat asks something: a question mark, or opens with a question word.

    Args:
        text: The beat's narration.

    Returns:
        True for a question.
    """
    first = tokenize(text)[:1]
    return "?" in text or (bool(first) and first[0] in QUESTION_OPENERS)


def unit_parents(beats: list[ScriptBeat]) -> dict[str, str | None]:
    """Each unit's parent unit, from the first beat that names it.

    Args:
        beats: Beats in order.

    Returns:
        Unit id → parent unit id (None for the macro unit).
    """
    parents: dict[str, str | None] = {MACRO_UNIT: None}
    for b in beats:
        if b.unit not in parents:
            parents[b.unit] = b.parent or MACRO_UNIT
    return parents


def depth(unit: str, parents: dict[str, str | None]) -> int:
    """How deep a unit sits under the macro unit (the macro unit is 0).

    Args:
        unit: Unit id.
        parents: Unit parents.

    Returns:
        The depth.
    """
    d = 0
    while parents.get(unit):
        unit = parents[unit]
        d += 1
    return d


def role_share(timed: list[Timed], roles: tuple[str, ...], total: float) -> float:
    """The share of the video's time spent in beats of the given roles.

    Args:
        timed: Beats with times.
        roles: Narrative roles to count.
        total: Video length (s).

    Returns:
        A fraction from 0 to 1.
    """
    return sum(t.end - t.start for t in timed if t.beat.role in roles) / max(total, 1e-6)


def grammar_problems(timed: list[Timed], total: float, style: Style) -> list[Problem]:
    """Rules N1–N13: the chain of units under one central question.

    Args:
        timed: Beats with times, in order.
        total: Video length (s).
        style: The series' style.

    Returns:
        The problems found.
    """
    n = style.narrative
    problems: list[Problem] = []
    beats = [t.beat for t in timed]
    index = {b.id: i for i, b in enumerate(beats)}
    at = {t.beat.id: t for t in timed}
    parents = unit_parents(beats)

    q0 = next((t for t in timed if t.beat.role == "question" and t.beat.unit == MACRO_UNIT), None)
    if q0 is None:
        problems.append(Problem("no_central_question", "error", "script", detail="no question beat in u0"))
    else:
        if q0.start > n["intro_max_s"]:
            problems.append(Problem("late_central_question", "error", q0.beat.id,
                                    detail=f"at {q0.start:.0f} s, style allows {n['intro_max_s']} s"))
        if not is_question(q0.beat.say):
            problems.append(Problem("central_question_not_asked", "error", q0.beat.id))
        if n["hook_required"] and not any(b.role == "hook" for b in beats[:index[q0.beat.id]]):
            problems.append(Problem("no_hook", "warning", q0.beat.id, detail="no hook before the central question"))

    for unit in [u for u in parents if u != MACRO_UNIT]:
        members = [b for b in beats if b.unit == unit]
        turns = [b for b in members if b.role in TURN_ROLES]
        if not turns:
            problems.append(Problem("no_turn", "error", unit, detail="unit has no revelation or answer"))
            continue
        first_turn = index[turns[0].id]
        if not any(b.role in WORK_ROLES and index[b.id] < first_turn for b in members):
            problems.append(Problem("turn_without_work", "error", unit, detail="no setup, dig or attempt before its turn"))
        if depth(unit, parents) > n["max_depth"]:
            problems.append(Problem("too_deep", "warning", unit, detail=f"style allows depth {n['max_depth']}"))

    for b in beats:
        if b.role == "wall":
            problems += wall_problems(b, beats, at, index, parents, style)
        if b.role in TURN_ROLES:
            problems += turn_problems(b, beats, index, parents)

    turn_beats = [t for t in timed if t.beat.role in TURN_ROLES]
    minutes = max(total / 60, 1e-6)
    per10 = len(turn_beats) / minutes * 10
    low, high = n["turns_per_10min"]
    if not low <= per10 <= high:
        problems.append(Problem("turn_budget", "warning", "script", detail=f"{per10:.1f} turns per 10 min, style wants {low}-{high}"))
    revelations = [t for t in timed if t.beat.role == "revelation"]
    if len(revelations) > 0.2 * len(beats) or sum(t.end - t.start for t in revelations) > 0.2 * total:
        problems.append(Problem("revelation_inflation", "error", "script", detail="revelations over 20% of beats or time"))

    work, cashout = role_share(timed, WORK_ROLES, total), role_share(timed, ("consolidate",), total)
    if work < n["work_min"]:
        problems.append(Problem("little_work", "warning", "script",
                                detail=f"setup/dig/attempt {work:.0%}, style wants {n['work_min']:.0%}"))
    if cashout < n["cashout_min"]:
        problems.append(Problem("little_cashout", "warning", "script",
                                detail=f"consolidation {cashout:.0%}, style wants {n['cashout_min']:.0%}"))

    links = [b for b in beats if b.role in TURN_ROLES and b.link]
    if links and sum(b.link == "causal" for b in links) / len(links) < n["causal_min"]:
        problems.append(Problem("weak_links", "warning", "script", detail=f"style wants {n['causal_min']:.0%} causal links"))
    for b in links:
        if b.link == "jump" and n["jumps"] == "none":
            problems.append(Problem("jump", "error", b.id, detail="this style never jumps between units"))
        if b.link == "jump" and n["jumps"] == "roadmap_only" and not any(
                x.role == "bridge" for x in beats[:index[b.id]]):
            problems.append(Problem("jump_without_roadmap", "error", b.id))

    climaxes = [t for t in timed if t.beat.climax]
    if len(climaxes) != 1:
        problems.append(Problem("climax_count", "error", "script", detail=f"{len(climaxes)} beats marked climax, need exactly 1"))
    else:
        c = climaxes[0]
        if c.beat.role not in TURN_ROLES:
            problems.append(Problem("climax_not_turn", "error", c.beat.id))
        low, high = n["climax_range"]
        if not low <= c.start / max(total, 1e-6) <= high:
            problems.append(Problem("climax_position", "warning", c.beat.id,
                                    detail=f"at {c.start / total:.0%}, style wants {low:.0%}-{high:.0%}"))
        after = beats[index[c.beat.id] + 1:]
        if not any(b.role == "consolidate" for b in after) or not any(b.role == "payoff" for b in after):
            problems.append(Problem("climax_not_cashed", "warning", c.beat.id, detail="needs consolidation and a payoff after it"))

    problems += ending_problems(beats, q0.beat if q0 else None, style)
    return problems


def wall_problems(wall: ScriptBeat, beats: list[ScriptBeat], at: dict[str, Timed], index: dict[str, int],
                  parents: dict[str, str | None], style: Style) -> list[Problem]:
    """Rules N4–N5 for one wall: it is set up, stated, and resolved after real tension.

    Args:
        wall: The wall beat.
        beats: All beats in order.
        at: Beat id → timed beat.
        index: Beat id → position.
        parents: Unit parents.
        style: The series' style.

    Returns:
        The problems found.
    """
    problems = []
    if not wall.obstruction:
        problems.append(Problem("wall_without_obstruction", "error", wall.id))
    elif len(wall.obstruction.split()) > 15:
        problems.append(Problem("long_obstruction", "warning", wall.id, detail="state it in 15 words or fewer"))
    if wall.against is None or index[wall.against] >= index[wall.id]:
        problems.append(Problem("wall_against_nothing", "error", wall.id, detail="'against' must name an earlier beat"))
    text = wall.say.lower()
    if "?" not in text and not any(re.search(rf"\b{re.escape(m)}\b", text) for m in TURN_MARKERS):
        problems.append(Problem("unmarked_wall", "warning", wall.id, detail="no turn word (but, problem, can't...) or question"))
    resolver = next((b for b in beats if b.resolves == wall.id and b.role == "revelation"), None)
    if resolver is None:
        problems.append(Problem("unresolved_wall", "error", wall.id))
        return problems
    gap = at[resolver.id].start - at[wall.id].start
    low, high = style.narrative["tension_s"]
    between = beats[index[wall.id] + 1:index[resolver.id]]
    child = any(parents.get(b.unit) == wall.unit for b in between)
    if gap < low:
        problems.append(Problem("asserted_wall", "warning", wall.id, detail=f"resolved after {gap:.0f} s; give it at least {low} s"))
    elif gap > high and not child:
        problems.append(Problem("slack_wall", "warning", wall.id, detail=f"resolved after {gap:.0f} s without a sub-unit"))
    return problems


def turn_problems(turn: ScriptBeat, beats: list[ScriptBeat], index: dict[str, int],
                  parents: dict[str, str | None]) -> list[Problem]:
    """Rules N6–N7 for one revelation or answer: it resolves something, then gets cashed out.

    Args:
        turn: The revelation or answer beat.
        beats: All beats in order.
        index: Beat id → position.
        parents: Unit parents.

    Returns:
        The problems found.
    """
    problems = []
    target = next((b for b in beats if b.id == turn.resolves), None)
    wanted = ("question",) if turn.role == "answer" else ("wall", "attempt")
    if target is None or target.role not in wanted or index[target.id] >= index[turn.id]:
        problems.append(Problem("resolves_nothing", "error", turn.id,
                                detail=f"'resolves' must name an earlier {' or '.join(wanted)}"))
    elif target.unit != turn.unit and target.unit not in ancestors(turn.unit, parents):
        problems.append(Problem("resolves_elsewhere", "warning", turn.id, detail="resolves a beat outside its unit"))
    for b in beats[index[turn.id] + 1:]:
        if b.role == "consolidate":
            break
        if b.role == "wall":
            problems.append(Problem("no_cashout", "warning", turn.id, detail="next wall comes before any consolidation"))
            break
    return problems


def ancestors(unit: str, parents: dict[str, str | None]) -> list[str]:
    """The units above a unit, nearest first.

    Args:
        unit: Unit id.
        parents: Unit parents.

    Returns:
        Ancestor unit ids.
    """
    out = []
    while parents.get(unit):
        unit = parents[unit]
        out.append(unit)
    return out


def ending_problems(beats: list[ScriptBeat], q0: ScriptBeat | None, style: Style) -> list[Problem]:
    """Rule N12: the video ends on a payoff that calls back to the opening.

    Args:
        beats: All beats in order.
        q0: The central question beat, if any.
        style: The series' style.

    Returns:
        The problems found.
    """
    last = beats[-1]
    if last.role != "payoff":
        return [Problem("no_payoff", "error", last.id, detail="the last beat must be a payoff")]
    opening = " ".join(b.say for b in beats if b.role == "hook") + " " + (q0.say if q0 else "")
    keys = {w for w in tokenize(opening) if len(w) >= 5 and w not in STOPWORDS}
    if keys & set(tokenize(last.say)):
        return []
    if style.narrative["open_questions_ending"] and "?" in last.say:
        return []
    return [Problem("no_callback", "warning", last.id, detail="share a key word with the hook or the central question")]


def wording_problems(beats: list[ScriptBeat], style: Style) -> list[Problem]:
    """Rules N14–N15 and the narration rules: no LaTeX, no dialogue, numbers, evaluative words.

    Args:
        beats: All beats.
        style: The series' style.

    Returns:
        The problems found.
    """
    problems = []
    limit = style.narrative["revelation_questions_max"]
    for b in beats:
        if LATEX.search(b.say):
            problems.append(Problem("latex_in_narration", "error", b.id, detail="TTS reads it literally; write spoken math"))
        if not style.rules["narrated_dialogue"] and DIALOGUE.search(CLARIFYING_I_SAY.sub("", b.say)):
            problems.append(Problem("narrated_dialogue", "error", b.id, detail="no characters talking; voice the intuition yourself"))
        if not style.rules["exact_numbers"] and EXACT_NUMBER.search(b.say):
            problems.append(Problem("exact_number", "warning", b.id, detail="this style keeps exact results in SOURCE_NOTES"))
        if RUN_ON_NUMBER.search(b.say):
            problems.append(Problem("run_on_number", "warning", b.id,
                                    detail=f"{RUN_ON_NUMBER.search(b.say).group(0)!r} can be heard as one number"))
        if b.role == "revelation" and b.say.count("?") > limit:
            problems.append(Problem("questioning_revelation", "warning", b.id, detail="a revelation answers; it does not ask"))
        if b.role not in ("revelation", "payoff") and any(re.search(rf"\b{w}\b", b.say.lower()) for w in EVALUATIVE):
            problems.append(Problem("misplaced_praise", "warning", b.id, detail="evaluative words belong to revelations"))
    return problems


def speaker_problems(beats: list[ScriptBeat], total: float, style: Style,
                     transcript: Transcript | None) -> tuple[list[Problem], dict[str, float]]:
    """Measure the speaker profile and compare it with the style's targets.

    Text measures always; pace and pauses only once the narration is voiced.

    Args:
        beats: All beats.
        total: Video length (s), real or estimated.
        style: The series' style.
        transcript: The narration's words, or None before voicing.

    Returns:
        The problems (warnings) and the measured profile.
    """
    text = " ".join(b.say for b in beats)
    words = tokenize(text)
    per_1k = 1000 / max(len(words), 1)
    sent = sentences(text)
    minutes = max(total / 60, 1e-6)
    profile = {
        "sentence_words_mean": len(words) / max(len(sent), 1),
        "questions_per_min": sum(s.endswith("?") for s in sent) / minutes,
        "you_per_1k": sum(w in ("you", "your", "you're", "you've", "you'll", "you'd", "yourself") for w in words) * per_1k,
        "we_per_1k": sum(w in ("we", "us", "our", "let's", "we're", "we've", "we'll", "we'd") for w in words) * per_1k,
        "i_per_1k": sum(w in ("i", "me", "my", "i'm", "i've", "i'll", "i'd") for w in words) * per_1k,
        "contractions_per_1k": len(CONTRACTION.findall(text)) * per_1k,
    }
    if transcript is not None:
        spoken = transcript.words[-1].end - transcript.words[0].start
        gaps = [b.start - a.end for a, b in zip(transcript.words, transcript.words[1:], strict=False)]
        profile["wpm"] = len(transcript.words) / max(spoken / 60, 1e-6)
        profile["long_pauses_per_min"] = sum(g >= LONG_PAUSE_S for g in gaps) / max(spoken / 60, 1e-6)
    problems = []
    for metric, value in profile.items():
        low, high = style.speaker[metric]
        if not low <= value <= high:
            problems.append(Problem("speaker_profile", "warning", metric,
                                    detail=f"{value:.1f}, style wants {low:g}-{high:g}"))
    return problems, {k: round(v, 2) for k, v in profile.items()}


def misheard_numbers(script: Script, transcript: Transcript) -> list[Problem]:
    """Numbers the voice said that the script never wrote ("seventy too" heard as 72).

    Decimal fragments (Whisper writes 7.25 as "7" and ".25") are not numbers of their own.

    Args:
        script: The script.
        transcript: The narration's words.

    Returns:
        One warning per unexpected number, with when it is said.
    """
    written = {t for b in script.beats for t in matching_tokens(b.say) if t.isdigit()}
    problems = []
    for unit in transcript.units():
        fragment = transcript.words[unit.first].text.lstrip().startswith((".", ","))
        if unit.token.isdigit() and unit.token not in written and not fragment:
            at = transcript.words[unit.first].start
            problems.append(Problem("misheard_number", "warning", unit.token,
                                    detail="the voice says a number the script does not; reword and re-voice",
                                    intervals=[[at, transcript.words[unit.last].end]]))
    return problems


def count_number_mentions(text: str) -> int:
    """Count contiguous spoken numeric mentions (digits, words, or fractions), skipping years,
    bare 'one', model identifiers like 'GPT-2', and logarithm bases like 'base-two'.

    Args:
        text: Spoken narration.

    Returns:
        Number of numeric mentions.
    """
    return len(NUMBER_MENTION.findall(NON_QUANTITY.sub(" ", text)))


def count_exact_specs(text: str) -> int:
    """Count exact decimals, percentages and 3+-digit non-year specs in spoken narration.

    Args:
        text: Spoken narration.

    Returns:
        Number of exact-spec mentions.
    """
    return len(EXACT_SPEC.findall(text))


def number_problems(beats: list[ScriptBeat], style: Style) -> tuple[list[Problem], dict[str, float]]:
    """Guard against number-dumping and spec overload, calibrated to 24 reference videos.

    Evidence: ``docs/research/intuitive-derivation.md``.

    Args:
        beats: All beats.
        style: The series' style (reads optional ceilings from ``style.rules``).

    Returns:
        Warnings found, plus ``numbers_per_1k`` and ``exact_specs_per_1k`` metrics.
    """
    full_text = " ".join(b.say for b in beats)
    total_words = max(len(tokenize(full_text)), 1)
    per_1k = 1000 / total_words
    nums_per_1k = count_number_mentions(full_text) * per_1k
    specs_per_1k = count_exact_specs(full_text) * per_1k
    problems: list[Problem] = []

    max_nums = style.rules.get("max_numbers_per_1k")
    if max_nums is not None and nums_per_1k > float(max_nums):
        problems.append(Problem(
            "number_density", "warning", "script",
            detail=f"{nums_per_1k:.1f} numbers per 1k words, style wants <= {float(max_nums):g}; "
                   "keep secondary specs in SOURCE_NOTES and spend narration on the logic",
        ))

    max_specs = style.rules.get("max_exact_specs_per_1k")
    if max_specs is not None and specs_per_1k > float(max_specs):
        problems.append(Problem(
            "spec_overload", "warning", "script",
            detail=f"{specs_per_1k:.1f} exact specs per 1k words, style wants <= {float(max_specs):g}; "
                   "reserve exact benchmarks for the wall and payoff",
        ))

    beat_limit = style.rules.get("max_beat_numbers")
    if beat_limit is not None:
        for b in beats:
            n_words = max(len(tokenize(b.say)), 1)
            n_nums = count_number_mentions(b.say)
            if n_nums >= int(beat_limit) and (n_nums / n_words * 100) >= BEAT_NUMBER_RATE_MIN:
                problems.append(Problem(
                    "number_dump", "warning", b.id,
                    detail=f"{n_nums} numbers in {n_words} words; derive the idea first and keep lookup tables in SOURCE_NOTES",
                ))

    return problems, {"numbers_per_1k": round(nums_per_1k, 1), "exact_specs_per_1k": round(specs_per_1k, 1)}


def lint(script: Script, style: Style, transcript: Transcript | None) -> tuple[list[Problem], dict]:
    """Run every script rule.

    Args:
        script: The script.
        style: The series' style.
        transcript: The narration's words, or None before voicing.

    Returns:
        The problems and a summary (length, beats, measured profile).
    """
    timed, total = place_beats(script, style, transcript)
    beats = list(script.beats)
    problems = grammar_problems(timed, total, style) + wording_problems(beats, style)
    num_problems, num_metrics = number_problems(beats, style)
    problems += num_problems
    if transcript is not None:
        problems += misheard_numbers(script, transcript)
    speaker, profile = speaker_problems(beats, total, style, transcript)
    profile.update(num_metrics)
    return problems + speaker, {"seconds": round(total, 1), "voiced": transcript is not None,
                                "beats": len(script.beats), "profile": profile}
