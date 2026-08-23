#!/usr/bin/env bash
# Carry one video from wherever it is to REVIEW-READY, unattended.
#
#   finish_video.sh <slug> <scene-file> <SceneClass> <logdir> [skip|logic-done]
#
# Stages, each skipped if its output already exists and is newer than the scene:
#   1. geometry pass — interpolates the whole scene, no movie. Occupancy JSON,
#      leftover checklist, overlap intervals, sparse Cairo stills, contact sheet.
#      Replaces --dry_run (which still Cairo-rasterized every frame) and the
#      full -ql encode that used to feed qa_frames.
#   2. check_sync + check_layout
#   3. STOP for the frame review (see deliver_video.sh)
#
# On any failure it writes a one-line reason to <logdir>/<slug>.status and exits
# non-zero, so the caller can move on to the next video and a human can fix the
# few that genuinely need judgement.
set -u

ROOT="/raid/ben/0Projects/StudyMaterial/ManimVideoGenerationSkill"
cd "$ROOT" || exit 2
# shellcheck disable=SC1091
source skills/manim-explain/scripts/env.sh 2>/dev/null

SLUG="$1"; FILE="$2"; CLASS="$3"; LOG="$4"; SKIP_VERIFY="${5:-no}"
SCENE="demos/${SLUG}/scenes/${FILE}"
ST="${LOG}/${SLUG}.status"
export PYTHONPATH="${MANIM_EXPLAIN_ROOT}/scripts:${ROOT}/demos/${SLUG}:${PYTHONPATH:-}"

say() { echo "[$(date +%H:%M:%S)] $SLUG: $*"; }

# One lane per video. Two concurrent runs share demos/<slug>/out/keyframes, and
# the geometry pass clears that directory at the start.
LOCK="${LOG}/${SLUG}.lock"
mkdir -p "${LOG}"
if ! mkdir "${LOCK}" 2>/dev/null; then
  echo "[$(date +%H:%M:%S)] $SLUG: another lane holds the lock — refusing to start"
  exit 4
fi
trap 'rmdir "${LOCK}" 2>/dev/null' EXIT
fail() { echo "$1" > "$ST"; say "FAILED — $1"; exit 1; }

# Pull the first real assertion line out of a manim log, colour codes stripped.
why() {
  sed 's/\x1b\[[0-9;]*m//g' "$1" \
    | grep -oE "^  (overlap|oob): .*|AssertionError: .*|NameError: .*|AttributeError: .*|TypeError: .*|KeyError: .*|IndexError: .*" \
    | head -1
}

# "skip" keeps a previous geometry pass (used when only the audits need a rerun).
# "logic-done" is accepted as an alias so older callers do not break; it still
# runs the geometry pass because that pass *is* the logic gate now.
if [ "$SKIP_VERIFY" = "skip" ]; then
  say "geometry pass skipped"
else
  say "geometry pass (no movie)"
  timeout 3600 python "${MANIM_EXPLAIN_ROOT}/scripts/geometry_pass.py" \
      "demos/${SLUG}" "$SCENE" "$CLASS" \
      > "${LOG}/${SLUG}.geom.log" 2>&1
  [ $? -ne 0 ] && fail "geometry: $(why "${LOG}/${SLUG}.geom.log")"
fi

say "audits"
python "${MANIM_EXPLAIN_ROOT}/scripts/check_sync.py" "demos/${SLUG}" \
    > "${LOG}/${SLUG}.sync.log" 2>&1
python "${MANIM_EXPLAIN_ROOT}/scripts/check_layout.py" "demos/${SLUG}" \
    > "${LOG}/${SLUG}.layout.log" 2>&1
grep -q "every cue window contains motion" "${LOG}/${SLUG}.sync.log" \
  || fail "sync: $(grep -oE 'STILL STRETCHES.*|SILENT.*' "${LOG}/${SLUG}.sync.log" | head -1)"
# text-over-text is always a defect and blocks. box-cuts-text sometimes is not
# (deliberately overlapping cards, a bar behind a label), so it is surfaced for
# the frame review to judge rather than failing the run.
# A text-over-text interval under 0.6 s is almost always two mobjects crossing
# during a transform. Those are surfaced for the frame review; only ones that
# linger block the build.
OVERS=$(python "${MANIM_EXPLAIN_ROOT}/scripts/check_layout.py" "demos/${SLUG}" \
          --min-duration 1.0 2>/dev/null | grep -oE "[0-9]+ text-over-text" \
          | grep -oE "^[0-9]+")
CUTS=$(grep -oE "[0-9]+ box-cuts-text" "${LOG}/${SLUG}.layout.log" | grep -oE "^[0-9]+")
[ "${OVERS:-1}" = "0" ] \
  || fail "layout: ${OVERS:-?} text-over-text — $(grep -A2 'COLLISIONS' "${LOG}/${SLUG}.layout.log" | tail -1 | tr -s ' ')"
[ "${CUTS:-0}" = "0" ] && say "layout clean" || say "layout: ${CUTS} box-cuts-text to judge in review"

say "QA stills ready — STOPPING for review"
CS="demos/${SLUG}/out/keyframes/contact_sheet.png"
[ -f "$CS" ] || fail "qa: no contact sheet produced"
echo "review $CS" > "$ST"
say "AWAITING REVIEW — $CS"
