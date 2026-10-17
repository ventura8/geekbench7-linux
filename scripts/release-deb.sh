#!/usr/bin/env bash
# Build geekbench7-linux .deb into artifacts/ (dpkg-buildpackage + lintian).
# Runs inside docker/Dockerfile.deb.
set -euo pipefail

cd "$(dirname "$0")/.."
# shellcheck source=release-common.sh
. scripts/release-common.sh

VERSION="$(gb_read_version)"
gb_prepare_artifacts_dir

WORK="$(mktemp -d /tmp/gb-deb.XXXXXX)"
trap 'rm -rf "${WORK}"' EXIT
gb_create_source_tarball "${VERSION}" "${WORK}/geekbench7-linux-${VERSION}.tar.gz"
tar -C "${WORK}" -xzf "${WORK}/geekbench7-linux-${VERSION}.tar.gz"

changelog_version="$(dpkg-parsechangelog -l "${WORK}/geekbench7-linux-${VERSION}/debian/changelog" -S Version)"
if [[ "${changelog_version}" != "${VERSION}" ]]; then
  echo "error: debian/changelog is at ${changelog_version}, VERSION is ${VERSION}" >&2
  exit 1
fi

codename="$(sed -n 's/^VERSION_CODENAME=//p' /etc/os-release | tr -d '"')"
if [[ -n "${codename}" ]]; then
  sed -i "1s/) [a-z]*;/) ${codename};/" "${WORK}/geekbench7-linux-${VERSION}/debian/changelog"
fi

echo "==> dpkg-buildpackage (binary, unsigned, no dbgsym)"
(cd "${WORK}/geekbench7-linux-${VERSION}" &&
  DEB_BUILD_OPTIONS="${DEB_BUILD_OPTIONS:+${DEB_BUILD_OPTIONS} }noautodbgsym" dpkg-buildpackage -us -uc -b)

arch="$(dpkg --print-architecture)"
DEB="${WORK}/geekbench7-linux_${VERSION}_${arch}.deb"
CHANGES="${WORK}/geekbench7-linux_${VERSION}_${arch}.changes"
[[ -f "${DEB}" ]] || {
  echo "error: expected ${DEB}" >&2
  exit 1
}

if command -v lintian >/dev/null 2>&1; then
  echo "==> lintian"
  chmod -R a+rX "${WORK}"
  lintian_cmd=(lintian --fail-on error --display-info "${CHANGES}")
  if [[ "$(id -u)" == 0 ]] && id nobody >/dev/null 2>&1; then
    runuser -u nobody -- env HOME=/tmp "${lintian_cmd[@]}"
  else
    "${lintian_cmd[@]}"
  fi
fi

gb_collect_artifacts_glob "${DEB}"
ls -la "${GB_ARTIFACTS_DIR}/"
