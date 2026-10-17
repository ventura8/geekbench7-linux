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
# Desktop + icon at AppDir root for appimagetool (Icon= name must match file stem).
DESKTOP_SRC="$STAGE/AppDir/usr/share/applications/io.github.ventura8.Geekbench7Linux.desktop"
ICON_SRC="$STAGE/AppDir/usr/share/icons/hicolor/scalable/apps/io.github.ventura8.Geekbench7Linux.svg"
if [[ -f "$DESKTOP_SRC" ]]; then
  cp "$DESKTOP_SRC" "$STAGE/AppDir/io.github.ventura8.Geekbench7Linux.desktop"
fi
if [[ -f "$ICON_SRC" ]]; then
  cp "$ICON_SRC" "$STAGE/AppDir/io.github.ventura8.Geekbench7Linux.svg"
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
  # Pure-script AppDir has no ELF for arch detection — set ARCH explicitly.
  ARCH="${ARCH}" "${APPIMAGETOOL}" "${RUNTIME_ARGS[@]}" "$STAGE/AppDir" "$OUT_DIR/$NAME"
  ls -la "$OUT_DIR/$NAME"
else
  echo "error: appimagetool not found" >&2
  exit 1
fi
