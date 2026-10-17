#!/usr/bin/env bash
# Build geekbench7-linux Arch package into artifacts/ (makepkg).
# Runs inside docker/Dockerfile.arch.
set -euo pipefail

cd "$(dirname "$0")/.."
# shellcheck source=release-common.sh
. scripts/release-common.sh

VERSION="$(gb_read_version)"
gb_prepare_artifacts_dir

WORK="$(mktemp -d /tmp/gb-makepkg.XXXXXX)"
trap 'rm -rf "${WORK}"' EXIT
TARBALL="geekbench7-linux-${VERSION}.tar.gz"
gb_create_source_tarball "${VERSION}" "${WORK}/${TARBALL}"
SHA256="$(sha256sum "${WORK}/${TARBALL}" | awk '{print $1}')"
gb_render_pkgbuild "${VERSION}" "${TARBALL}" "${SHA256}" >"${WORK}/PKGBUILD"

run_as_builder() {
  if [[ "$(id -u)" == 0 ]]; then
    chown -R builder:builder "${WORK}"
    runuser -u builder -- env HOME="${WORK}/home" "$@"
  else
    env HOME="${WORK}/home" "$@"
  fi
}

mkdir -p "${WORK}/home"
if [[ "$(id -u)" == 0 ]]; then
  pacman -S --needed --noconfirm meson ninja python desktop-file-utils appstream curl
fi

echo "==> makepkg"
(cd "${WORK}" && run_as_builder env BUILDDIR="${WORK}/build" PKGDEST="${WORK}" SRCDEST="${WORK}" \
  makepkg --noconfirm --cleanbuild)

gb_collect_artifacts_glob "${WORK}/geekbench7-linux-${VERSION}-*-x86_64.pkg.tar.zst" \
  "${WORK}/geekbench7-linux-${VERSION}-*-aarch64.pkg.tar.zst"
# Also keep a rendered PKGBUILD for AUR users browsing the release.
cp -a "${WORK}/PKGBUILD" "${GB_ARTIFACTS_DIR}/PKGBUILD"
ls -la "${GB_ARTIFACTS_DIR}/"
