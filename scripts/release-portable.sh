#!/usr/bin/env bash
# Build portable artifacts: tarball | appimage | flatpak | snap
set -euo pipefail
# shellcheck source=release-common.sh
source "$(cd "$(dirname "$0")" && pwd)/release-common.sh"
MODE="${1:?usage: release-portable.sh tarball|appimage|flatpak|snap}"
case "$MODE" in
  tarball)
    gb_make_src_tarball
    cp "$GB_ROOT/install.sh" "$GB_ARTIFACTS/"
    cp "$GB_ROOT/uninstall.sh" "$GB_ARTIFACTS/"
    ;;
  appimage)
    bash "$GB_ROOT/packaging/appimage/build-appimage.sh"
    ;;
  flatpak)
    if command -v flatpak-builder >/dev/null 2>&1; then
      flatpak-builder --force-clean --repo="$GB_ARTIFACTS/flatpak-repo" \
        "$GB_ARTIFACTS/flatpak-build" \
        "$GB_ROOT/packaging/flatpak/io.github.ventura8.Geekbench7Linux.yml"
      flatpak build-bundle "$GB_ARTIFACTS/flatpak-repo" \
        "$GB_ARTIFACTS/geekbench7-linux-${GB_VERSION}.flatpak" \
        io.github.ventura8.Geekbench7Linux
    else
      echo "flatpak-builder not available" >&2
    fi
    ;;
  snap)
    if command -v snapcraft >/dev/null 2>&1; then
      (cd "$GB_ROOT/packaging/snap" && snapcraft)
      cp -a "$GB_ROOT/packaging/snap"/*.snap "$GB_ARTIFACTS/" 2>/dev/null || true
    else
      echo "snapcraft not available" >&2
    fi
    ;;
  *) echo "unknown mode $MODE" >&2; exit 2 ;;
esac
