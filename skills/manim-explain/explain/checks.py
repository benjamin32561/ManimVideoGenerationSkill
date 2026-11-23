"""Static plan checks: what can be judged from the layout, the timeline and the style alone.

The geometry checks that need the scene to run are in ``probe``. Both report ``Problem``s.

* ``text_too_small`` (error): below the style's minimum.
* ``lone_symbol_text`` (error): a text that is only +, −, × or =; font glyphs that small are
  hairlines, so draw it as a ``symbol`` object.
* ``too_many_words`` (error): over the style's word budget for the text's role.
* ``not_uppercase`` (error): a role the style writes in capitals (Welch labels) is not.
* ``short_dwell`` (warning): unspoken text leaves before it can be read twice
  (``max(1.5 s, 0.6 s per word)``).
* ``texts_enter_together`` (warning): two separate text entrances in one event; one text
  entering at a time keeps the eye on one thing.
"""

from explain.plan import ENTRANCES, Layout, Timeline
from explain.problems import Problem
from explain.styles import Style
from explain.timing import Transcript, tokenize

SYMBOLS = {"+", "-", "−", "×", "÷", "=", "·"}
EXITS = ("fade_out", "dim")
DWELL_MIN_S = 1.5
DWELL_PER_WORD_S = 0.6
SPOKEN_WINDOW_S = 4.0


def text_role(spec: dict) -> str:
    """The role a text plays, for its word budget: ``role``, else its size role, else default.

    Args:
        spec: A text object's layout entry.

    Returns:
        The role name.
    """
    if spec.get("role"):
        return spec["role"]
    return spec["size"] if isinstance(spec["size"], str) else "default"


def size_problems(layout: Layout, style: Style) -> list[Problem]:
    """Check sizes, word budgets and capitals of every text and math object.

    Args:
        layout: The layout plan.
        style: The series' style.

    Returns:
        The problems found.
    """
    policy = style.text
    problems = []
    for oid, spec in layout.objects.items():
        if spec["type"] not in ("text", "math"):
            continue
        size = policy.roles[spec["size"]] if isinstance(spec["size"], str) else float(spec["size"])
        if size < policy.min_px:
            problems.append(Problem("text_too_small", "error", oid, detail=f"under {policy.min_px:g} px"))
        if spec["type"] != "text":
            continue
        content = spec["content"].strip()
        if content in SYMBOLS:
            problems.append(Problem("lone_symbol_text", "error", oid, detail="draw it as a `symbol` object"))
        role = text_role(spec)
        budget = policy.max_words.get(role, policy.max_words["default"])
        if len(content.split()) > budget:
            problems.append(Problem("too_many_words", "error", oid, detail=f"{role} allows {budget}"))
        if role in policy.uppercase_roles and content != content.upper():
            problems.append(Problem("not_uppercase", "error", oid, detail=f"{role} is written in capitals"))
    return problems


def timeline_problems(layout: Layout, timeline: Timeline, transcript: Transcript, style: Style) -> list[Problem]:
    """Check reading time of unspoken texts and how many texts enter per event.

    Args:
        layout: The layout plan.
        timeline: The resolved events.
        transcript: The narration's words (to tell spoken labels from unspoken ones).
        style: The series' style.

    Returns:
        The problems found.
    """
    problems = []
    entered: dict[str, float] = {}
    for event in timeline.events:
        t0 = event.start + style.motion.start_offset
        text_entrances = 0
        for action in event.actions:
            kind = action["action"]
            if kind in ENTRANCES or kind in ("copy_to", "morph"):
                ids = layout.leaves(action.get("targets") or [action["target"]])
                texts = [i for i in ids if i in layout.objects and layout.objects[i]["type"] == "text"]
                text_entrances += bool(texts)
                entered.update(dict.fromkeys(texts, t0))
            if kind in EXITS or kind == "morph":
                for leaf in layout.leaves(action.get("targets") or [action["source"]]):
                    if leaf in entered:
                        check_dwell(leaf, layout.objects[leaf]["content"], entered.pop(leaf), t0,
                                    transcript, problems)
        if text_entrances > 1:
            problems.append(Problem("texts_enter_together", "warning", event.id, intervals=[[t0, t0]]))
    return problems


def check_dwell(leaf: str, content: str, shown: float, gone: float, transcript: Transcript,
                problems: list[Problem]) -> None:
    """Flag an unspoken text that leaves before it can be read twice.

    A text counts as spoken when at least half its words are heard within a few seconds of
    its entrance; the voice reads it for the viewer, so it needs no extra dwell.

    Args:
        leaf: The text's id.
        content: Its words.
        shown: When it entered (s).
        gone: When it starts to leave or dim (s).
        transcript: The narration's words.
        problems: List to append a problem to.
    """
    words = tokenize(content)
    nearby = (x.text for x in transcript.words if abs(x.start - shown) <= SPOKEN_WINDOW_S)
    heard = {token for text in nearby for token in tokenize(text)}
    if words and sum(w in heard for w in words) * 2 >= len(words):
        return
    needed = max(DWELL_MIN_S, DWELL_PER_WORD_S * len(words))
    if gone - shown < needed:
        problems.append(Problem("short_dwell", "warning", leaf, detail=f"needs {needed:.1f} s", intervals=[[shown, gone]]))
