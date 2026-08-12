#!/usr/bin/env bash
# Source before Manim renders or skill Python scripts.
#   source <skill>/scripts/env.sh
#
# Portable: the skill may live in this repo, in ~/.claude/skills, ~/.cursor/skills,
# or a plugin cache. The *project* (demos, .env) is a separate tree — usually cwd.

# Skill root = the directory holding SKILL.md (parent of this scripts/ dir)
_THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export MANIM_EXPLAIN_ROOT="$(cd "${_THIS_DIR}/.." && pwd)"

# Project root = the tree you are working in (git root, else cwd)
if [[ -z "${MANIM_EXPLAIN_PROJECT:-}" ]]; then
  MANIM_EXPLAIN_PROJECT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
fi
export MANIM_EXPLAIN_PROJECT

# Load .env from the project, then from the skill root as a fallback
for _env_file in "${MANIM_EXPLAIN_PROJECT}/.env" "${MANIM_EXPLAIN_ROOT}/.env"; do
  if [[ -f "${_env_file}" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "${_env_file}"
    set +a
    break
  fi
done

# Optional no-sudo dvisvgm/ghostscript unpacked under <project>/.local
# (see scripts/setup_dvisvgm_local.sh in the ManimVideoGenerationSkill repo)
for _local in "${MANIM_EXPLAIN_PROJECT}/.local" "${MANIM_EXPLAIN_ROOT}/.local"; do
  if [[ -d "${_local}/usr/bin" ]]; then
    export PATH="${_local}/usr/bin:${PATH}"
    export LD_LIBRARY_PATH="${_local}/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-}"
    [[ -d "${_local}/usr/share/ghostscript/9.50/Resource/Init" ]] &&
      export GS_LIB="${_local}/usr/share/ghostscript/9.50/Resource/Init"
    break
  fi
done

# Manim environment: override MANIM_ENV for a different interpreter
if [[ -n "${MANIM_ENV:-}" && -d "${MANIM_ENV}/bin" ]]; then
  export PATH="${MANIM_ENV}/bin:${PATH}"
fi

export MANIM_EXPLAIN_TTS_MODEL="${MANIM_EXPLAIN_TTS_MODEL:-x-ai/grok-voice-tts-1.0}"
export MANIM_EXPLAIN_TTS_VOICE="${MANIM_EXPLAIN_TTS_VOICE:-leo}"
export MANIM_EXPLAIN_STT_MODEL="${MANIM_EXPLAIN_STT_MODEL:-openai/whisper-large-v3}"

# Sanity checks (warn only — docs-only work needs neither binary)
command -v manim >/dev/null 2>&1 ||
  echo "warn: manim not on PATH — set MANIM_ENV=/path/to/env or activate your environment" >&2
command -v dvisvgm >/dev/null 2>&1 ||
  echo "warn: dvisvgm not on PATH — MathTex will fail. Install texlive + dvisvgm." >&2
