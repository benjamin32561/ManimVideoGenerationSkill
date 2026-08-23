"""Turn sampled axis-aligned boxes into presence spans and leftover figures.

The geometry pass records, several times a second, every visible text and box
on stage. Collision checks already use those boxes; this module answers a
different question the AABB overlap test cannot: a figure that never collides
with anything, but was built in the first third of the video and is still on
stage in the last tenth. That is the leftover class that shipped into review
as arrows riding 130 s of empty space.

Identity is ``id()`` of the mobject during one walk of ``construct``. Labels
are for humans: many rectangles share the class name ``Rectangle``, so a
label-only span would merge them into one immortal figure.

Nothing here imports Manim. The sampler in ``layout_watch`` produces the
records; tests and ``geometry_pass`` consume them.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable, Mapping, Sequence

# A leftover appeared while the video was still introducing itself and is
# still present when the video is wrapping up. Closing recaps that are *meant*
# to survive will match too; the report is a checklist, not a verdict.
EARLY_FRAC = 0.35
LATE_FRAC = 0.90
# Persistent section titles live in this y-band for the whole video on purpose.
TITLE_BAND = (3.05, 3.95)
# Figures first seen before this are the standing machine (cores, bus, title)
# and are supposed to ride every later section fade.
STANDING_T = 12.0


def presence_spans(
    samples: Sequence[Mapping[str, Any]],
) -> dict[int, dict[str, Any]]:
    """Collapse occupancy samples into first-seen / last-seen per mobject id.

    Args:
        samples: Occupancy samples, each with a ``t`` time in seconds and an
            ``items`` list of dicts carrying ``id``, ``label``, ``kind``, and
            ``box``. Missing or malformed items are skipped.

    Returns:
        Mapping from mobject id to a record with ``label``, ``kind``,
        ``first``, ``last``, and ``hits`` (how many samples contained it).
    """
    spans: dict[int, dict[str, Any]] = {}
    for sample in samples:
        try:
            t = float(sample["t"])
        except (KeyError, TypeError, ValueError):
            continue
        for item in sample.get("items") or []:
            try:
                mob_id = int(item["id"])
            except (KeyError, TypeError, ValueError):
                continue
            record = spans.get(mob_id)
            if record is None:
                spans[mob_id] = {
                    "id": mob_id,
                    "label": str(item.get("label") or type(item).__name__),
                    "kind": str(item.get("kind") or "unknown"),
                    "first": t,
                    "last": t,
                    "hits": 1,
                    "box": item.get("box"),
                }
            else:
                record["last"] = t
                record["hits"] += 1
                if not record["label"] and item.get("label"):
                    record["label"] = str(item["label"])
    return spans


def leftover_records(
    samples: Sequence[Mapping[str, Any]],
    duration: float,
    *,
    early_frac: float = EARLY_FRAC,
    late_frac: float = LATE_FRAC,
) -> list[dict[str, Any]]:
    """Figures present in the opening stretch that are still on stage at the end.

    Section titles parked in the title band for the whole video are skipped;
    they are meant to survive.

    Args:
        samples: Occupancy samples as produced by :func:`presence_spans`.
        duration: Length of the walk in seconds. Spans with ``duration`` too
            small to have an early and a late window are empty.
        early_frac: Fraction of duration before which a leftover must first
            appear. Default 0.35.
        late_frac: Fraction of duration after which a leftover must still be
            present. Default 0.90.

    Returns:
        Leftover records sorted by how long they occupied the stage, longest
        first. Empty when ``duration`` is not positive.
    """
    if duration <= 0.0:
        return []
    early_cut = early_frac * duration
    late_cut = late_frac * duration
    leftovers: list[dict[str, Any]] = []
    for record in presence_spans(samples).values():
        if record["first"] > early_cut:
            continue
        if record["last"] < late_cut:
            continue
        box = record.get("box") or []
        if len(box) >= 4:
            cy = (float(box[1]) + float(box[3])) / 2.0
            if TITLE_BAND[0] <= cy <= TITLE_BAND[1]:
                continue
        ride = round(record["last"] - record["first"], 3)
        leftovers.append(
            {
                "id": record["id"],
                "label": record["label"],
                "kind": record["kind"],
                "first": round(record["first"], 3),
                "last": round(record["last"], 3),
                "duration": ride,
                "hits": record["hits"],
            }
        )
    leftovers.sort(key=lambda row: -row["duration"])
    return leftovers


def boundary_leftovers(
    samples: Sequence[Mapping[str, Any]],
    *,
    drop_frac: float = 0.35,
    min_drop: int = 4,
    survive: float = 2.0,
) -> list[dict[str, Any]]:
    """Figures that ride across a mass-disappear (a section boundary).

    A section change in these videos is a fade of many mobjects at once. The
    standing machine (cores, interconnect) is supposed to survive those fades.
    Only figures first seen after :data:`STANDING_T` *and* after the previous
    boundary, still present ``survive`` seconds later, are leftovers from the
    section just torn down. Title-band figures are skipped.

    Args:
        samples: Occupancy samples in time order.
        drop_frac: Fraction of the previous sample's ids that must vanish to
            count as a boundary.
        min_drop: Absolute number of ids that must vanish. Guards against a
            four-item scene losing two chips.
        survive: Seconds after the drop an id must still be on stage.

    Returns:
        Leftover records with a ``boundary`` time, longest-lived first.
    """
    if len(samples) < 3:
        return []
    ordered = sorted(samples, key=lambda s: float(s.get("t") or 0.0))
    result: dict[int, dict[str, Any]] = {}
    prev_ids: set[int] = set()
    prev_meta: dict[int, Mapping[str, Any]] = {}
    prev_t = 0.0
    first_seen: dict[int, float] = {}
    last_boundary = 0.0
    for sample in ordered:
        try:
            t = float(sample["t"])
        except (KeyError, TypeError, ValueError):
            continue
        items = list(sample.get("items") or [])
        now_meta: dict[int, Mapping[str, Any]] = {}
        for item in items:
            try:
                mob_id = int(item["id"])
            except (KeyError, TypeError, ValueError):
                continue
            now_meta[mob_id] = item
            first_seen.setdefault(mob_id, t)
        now_ids = set(now_meta)
        gone = prev_ids - now_ids
        if prev_ids and len(gone) >= min_drop and len(gone) / len(prev_ids) >= drop_frac:
            later = [
                s for s in ordered
                if float(s.get("t") or 0.0) >= t + survive
            ]
            if later:
                later_ids = {
                    int(it["id"])
                    for it in (later[0].get("items") or [])
                    if "id" in it
                }
                for mob_id in prev_ids & later_ids:
                    if first_seen.get(mob_id, t) < STANDING_T:
                        continue
                    if first_seen.get(mob_id, t) <= last_boundary + 0.05:
                        continue
                    item = prev_meta.get(mob_id) or {}
                    box = item.get("box") or []
                    if len(box) >= 4:
                        cy = (float(box[1]) + float(box[3])) / 2.0
                        if TITLE_BAND[0] <= cy <= TITLE_BAND[1]:
                            continue
                    result[mob_id] = {
                        "id": mob_id,
                        "label": str(item.get("label") or "?"),
                        "kind": str(item.get("kind") or "unknown"),
                        "first": round(first_seen.get(mob_id, prev_t), 3),
                        "boundary": round(t, 3),
                        "last": round(float(later[0].get("t") or t), 3),
                        "duration": round(
                            float(later[0].get("t") or t)
                            - first_seen.get(mob_id, prev_t),
                            3,
                        ),
                    }
            last_boundary = t
        prev_ids = now_ids
        prev_meta = now_meta
        prev_t = t
    rows = sorted(result.values(), key=lambda r: -r["duration"])
    return rows


def motion_events(
    samples: Sequence[Mapping[str, Any]],
    *,
    min_shift: float = 0.15,
) -> list[dict[str, Any]]:
    """AABB-centre moves between consecutive occupancy samples.

    This is the geometry-only answer to "what actually moved, and how far?"
    without reading pixels. A silent cue is a window with no motion events;
    a leftover that also never moved is a parked figure.

    Args:
        samples: Occupancy samples in time order. Each item needs ``id``,
            ``label``, and ``box`` ``(x0, y0, x1, y1)``.
        min_shift: Minimum centre displacement in scene units to count as
            motion. Smaller values pick up jitter from morph alignment.

    Returns:
        Records sorted by displacement, largest first, with ``id``, ``label``,
        ``t0``, ``t1``, ``shift``, and ``from`` / ``to`` centres.
    """
    ordered = sorted(samples, key=lambda s: float(s.get("t") or 0.0))
    prev_centre: dict[int, tuple[float, float, str, float]] = {}
    events: list[dict[str, Any]] = []
    for sample in ordered:
        try:
            t = float(sample["t"])
        except (KeyError, TypeError, ValueError):
            continue
        seen: set[int] = set()
        for item in sample.get("items") or []:
            try:
                mob_id = int(item["id"])
            except (KeyError, TypeError, ValueError):
                continue
            box = item.get("box") or []
            if len(box) < 4:
                continue
            cx = 0.5 * (float(box[0]) + float(box[2]))
            cy = 0.5 * (float(box[1]) + float(box[3]))
            label = str(item.get("label") or "?")
            seen.add(mob_id)
            prior = prev_centre.get(mob_id)
            if prior is not None:
                dx = cx - prior[0]
                dy = cy - prior[1]
                shift = (dx * dx + dy * dy) ** 0.5
                if shift >= min_shift:
                    events.append(
                        {
                            "id": mob_id,
                            "label": label,
                            "t0": prior[3],
                            "t1": t,
                            "shift": round(shift, 3),
                            "from": (round(prior[0], 3), round(prior[1], 3)),
                            "to": (round(cx, 3), round(cy, 3)),
                        }
                    )
            prev_centre[mob_id] = (cx, cy, label, t)
        # Drop ids that left the stage so a later respawn is not a teleport.
        for mob_id in list(prev_centre):
            if mob_id not in seen:
                prev_centre.pop(mob_id, None)
    events.sort(key=lambda row: -row["shift"])
    return events


def leftover_labels(
    samples: Sequence[Mapping[str, Any]],
    duration: float,
    **kwargs: Any,
) -> list[str]:
    """Human labels of leftover figures, longest-lived first.

    Args:
        samples: Occupancy samples.
        duration: Length of the walk in seconds.
        **kwargs: Forwarded to :func:`leftover_records`.

    Returns:
        Label strings. Duplicate labels (two rectangles) are kept; the caller
        can disambiguate from the full records.
    """
    return [row["label"] for row in leftover_records(samples, duration, **kwargs)]


def sample_at(
    samples: Sequence[Mapping[str, Any]],
    t: float,
) -> Mapping[str, Any] | None:
    """Return the occupancy sample nearest to ``t``.

    Args:
        samples: Occupancy samples with a ``t`` field.
        t: Scene time in seconds.

    Returns:
        The nearest sample, or ``None`` when ``samples`` is empty.
    """
    if not samples:
        return None
    return min(samples, key=lambda s: abs(float(s.get("t", 0.0)) - t))


def grouped_labels(items: Iterable[Mapping[str, Any]]) -> dict[str, list[str]]:
    """Group occupancy item labels by kind.

    Args:
        items: Occupancy items from one sample.

    Returns:
        ``{"text": [...], "frame": [...]}`` with unknown kinds under their
        own key. Empty kinds are omitted.
    """
    grouped: dict[str, list[str]] = defaultdict(list)
    for item in items:
        kind = str(item.get("kind") or "unknown")
        grouped[kind].append(str(item.get("label") or "?"))
    return dict(grouped)
