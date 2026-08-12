#!/usr/bin/env bash
# Unpack Ubuntu dvisvgm + deps into repo .local/ (no sudo).
# Run once per machine if MathTex fails with "dvisvgm not found".
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${REPO_ROOT}/.local"
TMP="${TMPDIR:-/tmp}/manim-explain-dvisvgm"
mkdir -p "$DEST" "$TMP"
cd "$TMP"

pkgs=(dvisvgm libwoff1 libgs9 libgs9-common libijs-0.35 libjbig2dec0 libidn11 libpaper1 libcups2 libcupsimage2)
apt-get download "${pkgs[@]}"
for deb in *.deb; do
  dpkg-deb -x "$deb" "$DEST"
done

echo "Installed into $DEST"
echo "Source skill env before rendering:"
echo "  source skills/manim-explain/scripts/env.sh"
