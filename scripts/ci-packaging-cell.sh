#!/usr/bin/env bash
# One packaging cell: build the Docker image, build the package, require artifacts.
# Usage: ./scripts/ci-packaging-cell.sh <format>
# Formats: deb rpm-fedora rpm-opensuse arch snap appimage flatpak tarball
#
# Env:
#   GB_DOCKER_PLATFORM  docker --platform (e.g. linux/amd64, linux/arm64, linux/riscv64)
#   GB_ARTIFACTS_DIR    output directory (default: artifacts/)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

FORMAT="${1:?usage: ci-packaging-cell.sh <deb|rpm-fedora|rpm-opensuse|arch|snap|appimage|flatpak|tarball>}"
export DOCKER_BUILDKIT=1
export GB_ARTIFACTS_DIR="${GB_ARTIFACTS_DIR:-${ROOT}/artifacts}"
PLATFORM="${GB_DOCKER_PLATFORM:-}"
[[ "${GB_ARTIFACTS_DIR}" == "${ROOT}"/* ]] || {
  echo "error: GB_ARTIFACTS_DIR must be inside ${ROOT}" >&2
  exit 1
}
mkdir -p "${GB_ARTIFACTS_DIR}"
ART_IN="/src/${GB_ARTIFACTS_DIR#"${ROOT}"/}"

# shellcheck source=release-common.sh
. scripts/release-common.sh
mapfile -t GIT_MOUNT < <(gb_git_mount_args)

DOCKER_FLAGS=()
PLATFORM_ARGS=()
BUILD_ARGS=()
if [[ -n "${PLATFORM}" ]]; then
  PLATFORM_ARGS=(--platform "${PLATFORM}")
  BUILD_ARGS=(--platform "${PLATFORM}")
fi

case "${FORMAT}" in
  deb)
    DOCKERFILE=docker/Dockerfile.deb IMAGE=geekbench7-linux-ci-deb:24.04
    BUILD=(./scripts/release-deb.sh)
    EXPECT=('*.deb')
    ;;
  rpm-fedora)
    DOCKERFILE=docker/Dockerfile.rpm.fedora IMAGE=geekbench7-linux-ci-rpm-fedora:44
    BUILD=(./scripts/release-rpm.sh fedora)
    EXPECT=('*.rpm')
    ;;
  rpm-opensuse)
    DOCKERFILE=docker/Dockerfile.rpm.opensuse IMAGE=geekbench7-linux-ci-rpm-opensuse:16.0
    BUILD=(./scripts/release-rpm.sh opensuse)
    EXPECT=('*.rpm')
    ;;
  arch)
    DOCKERFILE=docker/Dockerfile.arch IMAGE=geekbench7-linux-ci-arch:base-devel
    BUILD=(./scripts/release-arch.sh)
    EXPECT=('*.pkg.tar.zst')
    ;;
  tarball)
    DOCKERFILE=docker/Dockerfile.release IMAGE=geekbench7-linux-ci-release:24.04
    BUILD=(./scripts/release-portable.sh tarball)
    EXPECT=('geekbench7-linux-*-*.tar.gz' 'geekbench7-linux-*.tar.gz')
    ;;
  appimage)
    DOCKERFILE=docker/Dockerfile.release IMAGE=geekbench7-linux-ci-release:24.04
    BUILD=(./scripts/release-portable.sh appimage)
    EXPECT=('*.AppImage')
    ;;
  flatpak)
    DOCKERFILE=docker/Dockerfile.release IMAGE=geekbench7-linux-ci-release:24.04
    BUILD=(./scripts/release-portable.sh flatpak)
    DOCKER_FLAGS=(--privileged)
    EXPECT=('*.flatpak')
    ;;
  snap)
    DOCKERFILE="" IMAGE=""
    BUILD=()
    EXPECT=('*.snap')
    ;;
  *)
    echo "error: unknown packaging format: ${FORMAT}" >&2
    exit 2
    ;;
esac

echo "==> packaging cell ${FORMAT} platform=${PLATFORM:-host} (artifacts: ${GB_ARTIFACTS_DIR})"

if [[ "${FORMAT}" == snap ]]; then
  ./scripts/ci-snap-build.sh
else
  docker build "${BUILD_ARGS[@]}" -f "${DOCKERFILE}" -t "${IMAGE}" .
  # Override image USER so artifacts land as the host uid (writable mount).
  docker run --rm --user "$(id -u):$(id -g)" \
    "${DOCKER_FLAGS[@]}" "${PLATFORM_ARGS[@]}" \
    -e "GB_ARTIFACTS_DIR=${ART_IN}" \
    -e "GB_RPM_TARGET=${GB_RPM_TARGET:-}" \
    -e HOME=/tmp \
    -v "${ROOT}:/src:rw" "${GIT_MOUNT[@]}" -w /src \
    "${IMAGE}" "${BUILD[@]}"
fi

# Containers may write as root; reclaim ownership.
docker run --rm -v "${GB_ARTIFACTS_DIR}:/a" busybox:1.38.0 \
  chown -R "$(id -u):$(id -g)" /a >/dev/null 2>&1 || true

shopt -s nullglob
found=0
for pattern in "${EXPECT[@]}"; do
  for match in ${GB_ARTIFACTS_DIR}/${pattern}; do
    [[ -f "${match}" ]] || continue
    echo "  artifact: $(basename "${match}")"
    found=1
  done
done
shopt -u nullglob
if ((found == 0)); then
  echo "error: packaging cell ${FORMAT} produced no matching artifacts (${EXPECT[*]})" >&2
  ls -la "${GB_ARTIFACTS_DIR}" >&2 || true
  exit 1
fi
echo "==> packaging cell OK: ${FORMAT}"
