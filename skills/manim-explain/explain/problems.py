"""A problem found by any check step: the script lint, the plan check or the render check."""

from dataclasses import dataclass, field


@dataclass
class Problem:
    """Something a check found, and when it happens in the video.

    Attributes:
        kind: What is wrong (``text_overlap``, ``no_turn``, ``motion_outside_event``...).
        severity: ``error`` blocks the next step; ``warning`` goes to the review.
        subject: The beat, object or event at fault.
        other: The object it collides with, if any.
        detail: What limit was broken, in words.
        intervals: ``[[start, end], ...]`` in seconds; empty for problems without a time.
    """

    kind: str
    severity: str
    subject: str
    other: str | None = None
    detail: str = ""
    intervals: list[list[float]] = field(default_factory=list)
