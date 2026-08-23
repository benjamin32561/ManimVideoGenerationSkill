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

# Every invocation gets its own media tree. Two renders of the SAME scene
# otherwise share media/videos/<name>/<quality>/partial_movie_files/<Scene>/,
# and whichever reaches concatenation second dies on a missing
# partial_movie_file_list.txt — throwing away a full render. Different scenes
# were always independent; this makes same-scene concurrency safe too, so no
# caller has to coordinate.
RUN_MEDIA="${DEMO_DIR}/media/run_$$_$(date +%s)"
mkdir -p "${RUN_MEDIA}"
echo "manim ${QUALITY_ARGS[*]} ${SCENE_PY} ${SCENE_CLASS}  (media_dir ${RUN_MEDIA})"
# Parallel partial-movie encoders (0.21): overlap FFmpeg with the next play.
# Default.cfg ships at 1 (serial). This machine can keep several in flight.
manim --media_dir "${RUN_MEDIA}" --max-inflight-encoders "${MANIM_INFLIGHT:-4}" \
    "${QUALITY_ARGS[@]}" "${SCENE_PY}" "${SCENE_CLASS}"

# Locate newest mp4 — Manim may write under CWD media/ or demo media/
OUT_MP4="$(
  {
    find "${RUN_MEDIA}" -name "${SCENE_CLASS}.mp4" -printf '%T@ %p\n' 2>/dev/null || true
    find "${DEMO_DIR}/media/videos" -name "${SCENE_CLASS}.mp4" -printf '%T@ %p\n' 2>/dev/null || true
    find "${PWD}/media/videos" -name "${SCENE_CLASS}.mp4" -printf '%T@ %p\n' 2>/dev/null || true
  } | sort -nr | head -1 | cut -d' ' -f2-
)"
if [[ -z "${OUT_MP4}" ]]; then
  OUT_MP4="$(find "${DEMO_DIR}/media/videos" "${PWD}/media/videos" -name "${SCENE_CLASS}.mp4" 2>/dev/null | head -1 || true)"
fi

# Finished videos are delivered to
# <project>/output_videos/<series>/<slug>.mp4 — one file per demo, named after
# it, grouped by series. Everything else (stills, timeline, audio, partial
# renders) stays under demos/<slug>/.
SLUG="$(basename "${DEMO_DIR}")"
FINAL_MP4="$(python3 "${SCRIPT_DIR}/skill_paths.py" "${DEMO_DIR}")"
mkdir -p "${DEMO_DIR}/out" "$(dirname "${FINAL_MP4}")"
if [[ -n "${OUT_MP4}" && -f "${OUT_MP4}" ]]; then
  cp -f "${OUT_MP4}" "${FINAL_MP4}"
  echo "Delivered ${OUT_MP4} -> ${FINAL_MP4}"
  # The per-run tree is large (partial movie files); the deliverable is copied.
  rm -rf "${RUN_MEDIA}"
else
  echo "warn: could not find rendered ${SCENE_CLASS}.mp4 under media/" >&2
fi
