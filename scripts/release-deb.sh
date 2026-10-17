#!/usr/bin/env bash
# Build a .deb via dpkg-buildpackage (host or container).
set -euo pipefail
# shellcheck source=release-common.sh
source "$(cd "$(dirname "$0")" && pwd)/release-common.sh"
cd "$GB_ROOT"
dpkg-buildpackage -us -uc -b
arch="$(dpkg --print-architecture)"
cp -a ../geekbench7-linux_"${GB_VERSION}"_"${arch}".deb "$GB_ARTIFACTS/" || true
ls -la "$GB_ARTIFACTS"/*.deb 2>/dev/null || echo "deb build finished; copy artifacts manually if needed"
