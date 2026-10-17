#!/usr/bin/env bash
# Build a relocatable AppImage of the wrapper (no Geekbench binary inside).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VERSION="$(python3 "$ROOT/scripts/read-version.py")"
ARCH="$(uname -m)"
OUT_DIR="${GB_ARTIFACTS:-$ROOT/artifacts}"
mkdir -p "$OUT_DIR"
STAGE="$OUT_DIR/appimage-stage"
rm -rf "$STAGE"
meson setup "$STAGE/build" --prefix=/usr -Dflavor=appimage -Dpython="/usr/bin/env -S python3"
meson install -C "$STAGE/build" --destdir "$STAGE/AppDir"
install -Dm755 "$ROOT/packaging/appimage/AppRun" "$STAGE/AppDir/AppRun"
# Prefer appimagetool when available; otherwise ship a tarball of AppDir.
NAME="geekbench7-linux-${VERSION}-${ARCH}.AppImage"
if command -v appimagetool >/dev/null 2>&1; then
  UPDATE_INFO="gh-releases-zsync|ventura8|geekbench7-linux|latest|geekbench7-linux-*-${ARCH}.AppImage.zsync"
  export UPDATE_INFORMATION="$UPDATE_INFO"
  appimagetool "$STAGE/AppDir" "$OUT_DIR/$NAME"
else
  tar -C "$STAGE" -czf "$OUT_DIR/geekbench7-linux-${VERSION}-${ARCH}.AppDir.tar.gz" AppDir
  echo "appimagetool not found; wrote AppDir tarball instead" >&2
fi
