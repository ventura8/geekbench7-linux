#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=release-common.sh
source "$(cd "$(dirname "$0")" && pwd)/release-common.sh"
WORKDIR="$GB_ARTIFACTS/arch-build"
rm -rf "$WORKDIR"
mkdir -p "$WORKDIR"
tarball="$(gb_make_src_tarball)"
cp "$tarball" "$WORKDIR/geekbench7-linux-${GB_VERSION}.tar.gz"
sed "s/@VERSION@/${GB_VERSION}/g" "$GB_ROOT/packaging/arch/PKGBUILD.in" >"$WORKDIR/PKGBUILD"
(cd "$WORKDIR" && makepkg -f) || echo "makepkg unavailable; PKGBUILD rendered"
cp -a "$WORKDIR"/*.pkg.tar.* "$GB_ARTIFACTS/" 2>/dev/null || true
