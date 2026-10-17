#!/usr/bin/env bash
# Build geekbench7-linux RPM for fedora|opensuse into artifacts/.
# Usage: ./scripts/release-rpm.sh fedora|opensuse
set -euo pipefail

DISTRO="${1:?usage: release-rpm.sh fedora|opensuse}"
case "${DISTRO}" in
  fedora | opensuse) ;;
  *)
    echo "error: unknown distro ${DISTRO} (fedora or opensuse)" >&2
    exit 2
    ;;
esac

cd "$(dirname "$0")/.."
# shellcheck source=release-common.sh
. scripts/release-common.sh

VERSION="$(gb_read_version)"
gb_prepare_artifacts_dir

SPEC="packaging/rpm/${DISTRO}/geekbench7-linux.spec"
RPMTOP="$(mktemp -d /tmp/gb-rpmbuild.XXXXXX)"
trap 'rm -rf "${RPMTOP}"' EXIT
mkdir -p "${RPMTOP}"/{SOURCES,SPECS,RPMS,SRPMS,BUILD}
gb_create_source_tarball "${VERSION}" "${RPMTOP}/SOURCES/geekbench7-linux-${VERSION}.tar.gz"
cp "${SPEC}" "${RPMTOP}/SPECS/geekbench7-linux.spec"

DIST_ARGS=()
if [[ "${DISTRO}" == "opensuse" ]]; then
  DIST_ARGS=(-D "dist .lp160")
fi

rpmbuild -ba "${RPMTOP}/SPECS/geekbench7-linux.spec" \
  -D "gb_version ${VERSION}" \
  -D "_topdir ${RPMTOP}" \
  "${DIST_ARGS[@]}"

mapfile -t rpms < <(find "${RPMTOP}/RPMS" -name "geekbench7-linux-${VERSION}-*.rpm" -type f ! -name '*.src.rpm')
if ((${#rpms[@]} == 0)); then
  echo "error: no RPM produced for ${VERSION}" >&2
  find "${RPMTOP}/RPMS" -type f >&2 || true
  exit 1
fi

cp -a "${rpms[@]}" "${GB_ARTIFACTS_DIR}/"
ls -la "${GB_ARTIFACTS_DIR}/"

if command -v rpmlint >/dev/null 2>&1; then
  echo "==> rpmlint"
  lint_out="${RPMTOP}/rpmlint.txt"
  rpmlint "${rpms[@]}" >"${lint_out}" 2>&1 || true
  cat "${lint_out}"
  # Pure Python/Meson wrapper: "no-binary" is expected (scripts + data only).
  if grep -E ': E: ' "${lint_out}" | grep -vE 'no-binary' | grep -q .; then
    echo "error: rpmlint reported unexpected errors" >&2
    exit 1
  fi
fi
