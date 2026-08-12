#!/usr/bin/env bash
# Render a Manim scene and rely on add_sound for mux (Manim embeds audio).
# Usage:
#   source <skill>/scripts/env.sh
#   <skill>/scripts/render_and_mux.sh demos/<slug>/scenes/scene.py SceneName [-ql|-qh]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/env.sh"

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <scene.py> <SceneClass> [manim quality flags...]" >&2
  exit 2
fi

SCENE_PY="$1"
SCENE_CLASS="$2"
shift 2
QUALITY_ARGS=("${@:-"-qm"}")

DEMO_DIR="$(cd "$(dirname "${SCENE_PY}")/.." && pwd)"
export PYTHONPATH="${MANIM_EXPLAIN_ROOT}/scripts:${DEMO_DIR}:${PYTHONPATH:-}"

echo "manim ${QUALITY_ARGS[*]} ${SCENE_PY} ${SCENE_CLASS}"
manim "${QUALITY_ARGS[@]}" "${SCENE_PY}" "${SCENE_CLASS}"

# Locate newest mp4 — Manim may write under CWD media/ or demo media/
OUT_MP4="$(
  {
    find "${DEMO_DIR}/media/videos" -name "${SCENE_CLASS}.mp4" -printf '%T@ %p\n' 2>/dev/null || true
    find "${PWD}/media/videos" -name "${SCENE_CLASS}.mp4" -printf '%T@ %p\n' 2>/dev/null || true
  } | sort -nr | head -1 | cut -d' ' -f2-
)"
if [[ -z "${OUT_MP4}" ]]; then
  OUT_MP4="$(find "${DEMO_DIR}/media/videos" "${PWD}/media/videos" -name "${SCENE_CLASS}.mp4" 2>/dev/null | head -1 || true)"
fi

mkdir -p "${DEMO_DIR}/out"
if [[ -n "${OUT_MP4}" && -f "${OUT_MP4}" ]]; then
  cp -f "${OUT_MP4}" "${DEMO_DIR}/out/final.mp4"
  echo "Copied ${OUT_MP4} -> ${DEMO_DIR}/out/final.mp4"
else
  echo "warn: could not find rendered ${SCENE_CLASS}.mp4 under media/" >&2
fi
