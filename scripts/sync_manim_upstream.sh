#!/usr/bin/env bash
# Pull Manim Community's main into our vendored fork without discarding local patches.
#
#   scripts/sync_manim_upstream.sh          # fetch + merge upstream/main
#   scripts/sync_manim_upstream.sh fetch    # fetch only
#
# origin  = git@github.com-personal:benjamin32561/manim.git  (our fork)
# upstream = https://github.com/ManimCommunity/manim.git
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIM="${ROOT}/vendor/manim"

if [[ ! -d "${MANIM}/.git" && ! -f "${MANIM}/.git" ]]; then
  echo "vendor/manim is missing. From the repo root:" >&2
  echo "  git submodule update --init --recursive" >&2
  exit 2
fi

cd "${MANIM}"
if ! git remote get-url upstream >/dev/null 2>&1; then
  git remote add upstream https://github.com/ManimCommunity/manim.git
fi

git fetch origin
git fetch upstream

if [[ "${1:-merge}" == "fetch" ]]; then
  echo "Fetched. Local: $(git rev-parse --short HEAD)  upstream/main: $(git rev-parse --short upstream/main)"
  exit 0
fi

echo "Merging upstream/main into $(git rev-parse --abbrev-ref HEAD) @ $(git rev-parse --short HEAD)"
git merge --no-edit upstream/main
echo "Now at $(git rev-parse --short HEAD). Push the fork with: git push origin"
echo "Then record the new SHA in the parent repo: git add vendor/manim && git status"
