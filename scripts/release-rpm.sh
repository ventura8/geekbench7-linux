#!/usr/bin/env bash
# Build RPM for fedora|opensuse.
set -euo pipefail
# shellcheck source=release-common.sh
source "$(cd "$(dirname "$0")" && pwd)/release-common.sh"
DISTRO="${1:?usage: release-rpm.sh fedora|opensuse}"
SPEC="$GB_ROOT/packaging/rpm/${DISTRO}/geekbench7-linux.spec"
tarball="$(gb_make_src_tarball)"
mkdir -p "$HOME/rpmbuild/SOURCES" "$HOME/rpmbuild/SPECS"
cp "$tarball" "$HOME/rpmbuild/SOURCES/geekbench7-linux-${GB_VERSION}.tar.gz"
cp "$SPEC" "$HOME/rpmbuild/SPECS/"
rpmbuild -ba "$HOME/rpmbuild/SPECS/geekbench7-linux.spec" -D "gb_version ${GB_VERSION}"
cp -a "$HOME/rpmbuild/RPMS"/*/*.rpm "$GB_ARTIFACTS/" 2>/dev/null || true
cp -a "$HOME/rpmbuild/SRPMS"/*.rpm "$GB_ARTIFACTS/" 2>/dev/null || true
