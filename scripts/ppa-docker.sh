#!/usr/bin/env bash
# Build signed/unsigned source package for PPA upload (jammy/noble/resolute).
set -euo pipefail
# shellcheck source=release-common.sh
source "$(cd "$(dirname "$0")" && pwd)/release-common.sh"
SERIES="${1:-noble}"
echo "Building source package for $SERIES (wrapper only; no Geekbench binary)"
cd "$GB_ROOT"
dpkg-buildpackage -S -us -uc || dpkg-buildpackage -S -us -uc -d
echo "Source package built; upload with dput when PPA_UPLOAD is enabled"
