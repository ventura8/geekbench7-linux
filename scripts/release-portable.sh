#!/usr/bin/env bash
# Build portable artifacts: tarball | appimage | flatpak | snap
# Usage: ./scripts/release-portable.sh tarball|appimage|flatpak|snap
set -euo pipefail

cd "$(dirname "$0")/.."
# shellcheck source=release-common.sh
. scripts/release-common.sh

VERSION="$(gb_read_version)"
MODE="${1:?usage: release-portable.sh tarball|appimage|flatpak|snap}"
gb_prepare_artifacts_dir
ARCH="$(uname -m)"

build_tarball() {
  local work stage root out src
  # Source tree tarball (install.sh builds with meson into ~/.local).
  src="$(gb_make_src_tarball)"
  cp -a install.sh uninstall.sh "${GB_ARTIFACTS_DIR}/"
  echo "==> source tarball ${src}"

  # Relocatable prefix tarball (pre-built wrapper; no Geekbench binary).
  work="$(mktemp -d /tmp/gb-tarball.XXXXXX)"
  stage="${work}/stage"
  root="geekbench7-linux-${VERSION}"
  out="${GB_ARTIFACTS_DIR}/geekbench7-linux-${VERSION}-${ARCH}.tar.gz"
  echo "==> relocatable tarball ${out}"
  meson setup "${work}/build" --prefix="/${root}" --buildtype=release \
    -Dflavor=tarball -Dpython="${GB_PORTABLE_PYTHON}"
  meson compile -C "${work}/build"
  DESTDIR="${stage}" meson install -C "${work}/build" --no-rebuild
  install -D -m 0644 LICENSE "${stage}/${root}/share/doc/geekbench7-linux/LICENSE"
  install -D -m 0644 README.md "${stage}/${root}/share/doc/geekbench7-linux/README.md"
  tar -C "${stage}" --sort=name --owner=0 --group=0 --numeric-owner \
    --mtime="@${SOURCE_DATE_EPOCH:-0}" -czf "${out}" "${root}"
  rm -rf "${work}"
  ls -la "${src}" "${out}"
}

build_appimage() {
  local out="${GB_ARTIFACTS_DIR}/geekbench7-linux-${VERSION}-${ARCH}.AppImage"
  echo "==> AppImage ${out}"
  APPIMAGETOOL="${APPIMAGETOOL:-/usr/local/bin/appimagetool}" \
    packaging/appimage/build-appimage.sh
  [[ -f "${out}" ]] || {
    echo "error: expected ${out}" >&2
    exit 1
  }
  ls -la "${out}"
}

build_flatpak() {
  local app_id work bundle
  app_id="$(gb_app_id)"
  work="${GB_ARTIFACTS_DIR}/.flatpak-work"
  bundle="${GB_ARTIFACTS_DIR}/${app_id}-${VERSION}-${ARCH}.flatpak"
  echo "==> Flatpak ${bundle}"
  rm -rf "${work}"
  mkdir -p "${work}"
  gb_create_source_tarball "${VERSION}" "${work}/geekbench7-linux-src.tar.gz"
  cat >"${work}/${app_id}.yml" <<EOF
app-id: ${app_id}
runtime: org.freedesktop.Platform
runtime-version: '24.08'
sdk: org.freedesktop.Sdk
command: geekbench7-linux
finish-args:
  - --share=network
  - --filesystem=xdg-data
  - --filesystem=xdg-cache
  - --filesystem=xdg-config
modules:
  - name: geekbench7-linux
    buildsystem: meson
    config-opts:
      - -Dflavor=flatpak
      - -Dpython=/usr/bin/python3
      - -Dgeekbench_alias=true
    sources:
      - type: archive
        path: geekbench7-linux-src.tar.gz
EOF
  flatpak remote-add --user --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
  flatpak-builder --user --install-deps-from=flathub --disable-rofiles-fuse --force-clean \
    --state-dir="${work}/state" --repo="${work}/repo" "${work}/build" "${work}/${app_id}.yml"
  flatpak build-bundle "${work}/repo" "${bundle}" "${app_id}"
  rm -rf "${work}"
  ls -la "${bundle}"
}

build_snap() {
  local tarball="packaging/snap/geekbench7-linux-src.tar.gz"
  local snap_arch
  case "$(uname -m)" in
    x86_64) snap_arch=amd64 ;;
    aarch64 | arm64) snap_arch=arm64 ;;
    riscv64) snap_arch=riscv64 ;;
    *) snap_arch="$(uname -m)" ;;
  esac
  local snap="geekbench7-linux_${VERSION}_${snap_arch}.snap"
  echo "==> snap ${snap}"
  rm -f "${tarball}" "packaging/snap/${snap}"
  gb_create_source_tarball "${VERSION}" "${tarball}"
  # Keep snapcraft.yaml version in sync with VERSION.
  sed -i "s/^version: .*/version: '${VERSION}'/" packaging/snap/snapcraft.yaml
  (
    cd packaging/snap
    rm -rf parts stage prime overlay
    if command -v snapcraft >/dev/null 2>&1; then
      snapcraft pack --destructive-mode --output "${snap}"
    else
      echo "error: snapcraft not available" >&2
      exit 1
    fi
    rm -rf parts stage prime overlay
  )
  mv -f "packaging/snap/${snap}" "${GB_ARTIFACTS_DIR}/${snap}"
  rm -f "${tarball}"
  ls -la "${GB_ARTIFACTS_DIR}/${snap}"
}

case "${MODE}" in
  tarball) build_tarball ;;
  appimage) build_appimage ;;
  flatpak) build_flatpak ;;
  snap) build_snap ;;
  *)
    echo "usage: release-portable.sh tarball|appimage|flatpak|snap" >&2
    exit 2
    ;;
esac
