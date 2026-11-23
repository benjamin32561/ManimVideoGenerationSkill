"""Check reports: written by each check step, read by the steps they gate.

A report records the digest of what it checked, so a later step can refuse to run on inputs
that changed after the check (``require_passed``).
"""

import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from explain.problems import Problem


def digest_files(*paths: Path, extra: str = "") -> str:
    """Hash a set of files (names and contents), so a report can be tied to them.

    Args:
        *paths: The files; a missing file hashes as absent, so creating it changes the digest.
        extra: Anything else to fold in (a version, another digest).

    Returns:
        A hex SHA-256.
    """
    digest = hashlib.sha256(extra.encode())
    for path in paths:
        digest.update(Path(path).name.encode())
        digest.update(Path(path).read_bytes() if Path(path).is_file() else b"<absent>")
    return digest.hexdigest()


def write_report(path: Path, digest: str, problems: list[Problem], **extra: object) -> dict:
    """Write a check report and return it.

    Args:
        path: The report file.
        digest: The digest of what was checked (script, narration or plan).
        problems: Everything found.
        **extra: Step-specific fields (timings, frame lists...).

    Returns:
        The report as written.
    """
    report = {
        "digest": digest,
        "passed": not any(p.severity == "error" for p in problems),
        "errors": [asdict(p) for p in problems if p.severity == "error"],
        "warnings": [asdict(p) for p in problems if p.severity == "warning"],
        **extra,
    }
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n")
    return report


def require_passed(path: Path, digest: str, step: str) -> dict:
    """Load a report and insist it passed for the current inputs.

    Args:
        path: The report file.
        digest: The current digest of what the report checked.
        step: The command that writes the report, for the message.

    Returns:
        The report.

    Raises:
        SystemExit: If the report is missing, failed, or was made for different inputs.
    """
    if not Path(path).is_file():
        raise SystemExit(f"Run {step} first ({path.name} is missing).")
    report = json.loads(Path(path).read_text())
    if report["digest"] != digest:
        raise SystemExit(f"What {step} checked has changed since it ran; run it again.")
    if not report["passed"]:
        raise SystemExit(f"{step} found errors; fix them and run it again.")
    return report


def describe(problem: Problem) -> str:
    """One line for a problem: kind, what, with what, why, when.

    Args:
        problem: The problem.

    Returns:
        The line.
    """
    parts = [f"{problem.kind}: {problem.subject}"]
    if problem.other:
        parts.append(f"× {problem.other}")
    if problem.detail:
        parts.append(f"({problem.detail})")
    if problem.intervals:
        spans = ", ".join(f"{a:.2f}-{b:.2f}s" if b > a else f"{a:.2f}s" for a, b in problem.intervals[:4])
        more = f" +{len(problem.intervals) - 4} more" if len(problem.intervals) > 4 else ""
        parts.append(f"at {spans}{more}")
    return " ".join(parts)


def print_problems(title: str, problems: list[Problem]) -> None:
    """Print a step's problems, errors first.

    Args:
        title: The step's name.
        problems: Everything found.
    """
    errors = [p for p in problems if p.severity == "error"]
    warnings = [p for p in problems if p.severity == "warning"]
    print(f"{title}: {len(errors)} error(s), {len(warnings)} warning(s)")
    for p in errors:
        print(f"  ERROR   {describe(p)}")
    for p in warnings:
        print(f"  warning {describe(p)}")
