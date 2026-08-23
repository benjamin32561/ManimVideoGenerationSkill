#!/usr/bin/env bash
# Render one REVIEWED video at -qm and deliver it.
#
#   deliver_video.sh <slug> <scene-file> <SceneClass> <logdir>
#
# Run this only after the contact sheet at demos/<slug>/out/keyframes/ has
# actually been read, along with full frames for anything suspicious.
#
# finish_video.sh deliberately stops short of this step. Reading pixels is a
# judgement call a shell script cannot make, and every defect that mattered in
# this project passed both mechanical audits and was visible only in a frame.

# Caching is ON. Each invocation already has its own media_dir, so two -qm
# runs cannot share partial files. --disable_caching was leftover from the
# geometry walk, where it is forced so interpolation actually runs.
set -u
ROOT="/raid/ben/0Projects/StudyMaterial/ManimVideoGenerationSkill"
cd "$ROOT" || exit 2
# shellcheck disable=SC1091
source skills/manim-explain/scripts/env.sh 2>/dev/null

SLUG="$1"; FILE="$2"; CLASS="$3"; LOG="$4"
ST="${LOG}/${SLUG}.status"
export PYTHONPATH="${MANIM_EXPLAIN_ROOT}/scripts:${ROOT}/demos/${SLUG}:${PYTHONPATH:-}"

# HARD GATE. Not a formality: a shell script cannot look at a picture, so it
# must refuse to spend a final-quality render on frames nobody read. The gate
# also reopens if the scene was edited after the review, because a review is a
# statement about one specific set of frames.
if ! python "${MANIM_EXPLAIN_ROOT}/scripts/review_gate.py" "demos/${SLUG}" --check; then
  echo "review required" > "$ST"
  echo "[$(date +%H:%M:%S)] $SLUG: BLOCKED — read the frames, then record the verdict:"
  echo "    python \$MANIM_EXPLAIN_ROOT/scripts/review_gate.py demos/${SLUG} --record pass --frames N --notes '...'"
  exit 3
fi

echo "[$(date +%H:%M:%S)] $SLUG: -qm render (reviewed)"
timeout 10800 ./skills/manim-explain/scripts/render_and_mux.sh \
    "demos/${SLUG}/scenes/${FILE}" "$CLASS" -qm \
    > "${LOG}/${SLUG}.qm.log" 2>&1

FINAL="$(python3 skills/manim-explain/scripts/skill_paths.py "demos/${SLUG}")"
if [ ! -f "$FINAL" ]; then
  R=$(sed 's/\x1b\[[0-9;]*m//g' "${LOG}/${SLUG}.qm.log" \
      | grep -oE "^  (overlap|oob): .*|AssertionError: .*" | head -1)
  echo "qm failed: $R" > "$ST"
  echo "[$(date +%H:%M:%S)] $SLUG: QM FAILED — $R"
  exit 1
fi

DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$FINAL")
AUD=$(ffprobe -v error -select_streams a -show_entries stream=codec_name -of csv=p=0 "$FINAL")
echo "delivered ${DUR%.*}s audio=${AUD:-NONE}" > "$ST"
echo "[$(date +%H:%M:%S)] $SLUG: DELIVERED ${DUR%.*}s audio=${AUD:-NONE} -> $FINAL"
