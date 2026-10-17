#!/usr/bin/env bash
# Build a relocatable AppImage of the wrapper (no Geekbench binary inside).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VERSION="$(python3 "$ROOT/scripts/read-version.py")"
ARCH="$(uname -m)"
OUT_DIR="${GB_ARTIFACTS_DIR:-${GB_ARTIFACTS:-$ROOT/artifacts}}"
mkdir -p "$OUT_DIR"
STAGE="$OUT_DIR/appimage-stage"
rm -rf "$STAGE"
meson setup "$STAGE/build" --prefix=/usr --buildtype=release \
  -Dflavor=appimage -Dpython="/usr/bin/env -S python3"
meson compile -C "$STAGE/build"
DESTDIR="$STAGE/AppDir" meson install -C "$STAGE/build" --no-rebuild
install -Dm755 "$ROOT/packaging/appimage/AppRun" "$STAGE/AppDir/AppRun"
# Desktop + icon at AppDir root for appimagetool.
if [[ -f "$STAGE/AppDir/usr/share/applications/io.github.ventura8.Geekbench7Linux.desktop" ]]; then
  cp "$STAGE/AppDir/usr/share/applications/io.github.ventura8.Geekbench7Linux.desktop" \
    "$STAGE/AppDir/geekbench7-linux.desktop"
fi
ICON_SRC="$STAGE/AppDir/usr/share/icons/hicolor/scalable/apps/io.github.ventura8.Geekbench7Linux.svg"
if [[ -f "$ICON_SRC" ]]; then
  cp "$ICON_SRC" "$STAGE/AppDir/geekbench7-linux.svg"
fi

NAME="geekbench7-linux-${VERSION}-${ARCH}.AppImage"
APPIMAGETOOL="${APPIMAGETOOL:-appimagetool}"
if command -v "${APPIMAGETOOL}" >/dev/null 2>&1 || [[ -x "${APPIMAGETOOL}" ]]; then
  RUNTIME_ARGS=()
  for rt in "/opt/appimagetool/runtime-${ARCH}" /opt/appimagetool/runtime-x86_64 /opt/appimagetool/runtime-aarch64; do
    if [[ -f "${rt}" ]]; then
      RUNTIME_ARGS=(--runtime-file "${rt}")
      break
    fi
  done
  UPDATE_INFO="gh-releases-zsync|ventura8|geekbench7-linux|latest|geekbench7-linux-*-${ARCH}.AppImage.zsync"
  export UPDATE_INFORMATION="$UPDATE_INFO"
  "${APPIMAGETOOL}" "${RUNTIME_ARGS[@]}" "$STAGE/AppDir" "$OUT_DIR/$NAME"
  ls -la "$OUT_DIR/$NAME"
else
  echo "error: appimagetool not found" >&2
  exit 1
fi
