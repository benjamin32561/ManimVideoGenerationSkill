#!/usr/bin/env bash
# Source before running the pipeline:  source <skill>/scripts/env.sh
#
# Sets MANIM_EXPLAIN_ROOT (this skill) and MANIM_EXPLAIN_PROJECT (the tree you work in: the
# git root, else the current directory), loads the project's .env (OPENROUTER_API_KEY,
# MANIM_ENV), and puts the manimgx environment's bin/ first on PATH.

_THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export MANIM_EXPLAIN_ROOT="$(cd "${_THIS_DIR}/.." && pwd)"

if [[ -z "${MANIM_EXPLAIN_PROJECT:-}" ]]; then
  MANIM_EXPLAIN_PROJECT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
fi
export MANIM_EXPLAIN_PROJECT

if [[ -f "${MANIM_EXPLAIN_PROJECT}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${MANIM_EXPLAIN_PROJECT}/.env"
  set +a
fi

if [[ -n "${MANIM_ENV:-}" && -d "${MANIM_ENV}/bin" ]]; then
  export PATH="${MANIM_ENV}/bin:${PATH}"
fi

python -c "import manimgx" 2>/dev/null ||
  echo "error: manimgx is not importable; set MANIM_ENV in ${MANIM_EXPLAIN_PROJECT}/.env to an env with manimgx installed" >&2
[[ -n "${OPENROUTER_API_KEY:-}" ]] ||
  echo "error: OPENROUTER_API_KEY is not set (needed by voice.py)" >&2
