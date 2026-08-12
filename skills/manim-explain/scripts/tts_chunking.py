"""Shared TTS chunk grouping + per-boundary pause plan.

Pause craft: when VO must breathe after naming / introducing an object, split
into a new ``tts_chunk`` and set ``pause_after`` on that chunk's last beat.
Silence is baked into narration.mp3; Manim soft-idles in the matching gap.
Never insert naked scene.wait that desyncs from continuous speech.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


def chunk_plan(
    script: dict,
    *,
    prepare: Callable[[str], str] | None = None,
    chunk_by: str | None = None,
    default_gap: float | None = None,
) -> list[dict[str, Any]]:
    """Build ordered TTS pieces: [{key, text, pause_after}, ...].

    ``pause_after`` is silence inserted *after* this chunk when concatenating
    (0 for the final chunk). Defaults to ``tts.inter_chunk_silence``; override
    per beat with ``pause_after: 0.6`` (max across beats in the chunk wins).
    """
    tts_cfg = script.get("tts") or {}
    if default_gap is None:
        default_gap = float(tts_cfg.get("inter_chunk_silence", 0.35))
    if not chunk_by:
        chunk_by = tts_cfg.get("chunk_by")
    if prepare is None:

        def prepare(s: str) -> str:
            return s.strip()

    groups: list[dict[str, Any]] = []
    index: dict[str, int] = {}

    for beat in script.get("beats") or []:
        say = (beat.get("say") or "").strip()
        if not say:
            continue
        text = prepare(say)
        key = beat.get(chunk_by) if chunk_by else None
        if key is None or key == "":
            key = f"_beat_{beat.get('id', len(groups))}"
        key = str(key)
        pause = beat.get("pause_after")
        pause_f = float(pause) if pause is not None else None

        if key not in index:
            index[key] = len(groups)
            groups.append(
                {
                    "key": key,
                    "texts": [text],
                    "pause_after": pause_f if pause_f is not None else float(default_gap),
                }
            )
        else:
            g = groups[index[key]]
            g["texts"].append(text)
            if pause_f is not None:
                g["pause_after"] = max(float(g["pause_after"]), pause_f)

    out: list[dict[str, Any]] = []
    for i, g in enumerate(groups):
        pause_after = float(g["pause_after"]) if i < len(groups) - 1 else 0.0
        out.append(
            {
                "key": g["key"],
                "text": " ".join(g["texts"]),
                "pause_after": pause_after,
            }
        )
    return out


def chunk_texts(
    script: dict,
    *,
    prepare: Callable[[str], str] | None = None,
    chunk_by: str | None = None,
) -> list[str]:
    return [c["text"] for c in chunk_plan(script, prepare=prepare, chunk_by=chunk_by)]


def chunk_gaps(
    script: dict,
    *,
    prepare: Callable[[str], str] | None = None,
    chunk_by: str | None = None,
) -> list[float]:
    plan = chunk_plan(script, prepare=prepare, chunk_by=chunk_by)
    if len(plan) <= 1:
        return []
    return [float(c["pause_after"]) for c in plan[:-1]]
