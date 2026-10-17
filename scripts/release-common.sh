#!/usr/bin/env bash
# Shared helpers for release / packaging scripts (sourced, never executed).
set -euo pipefail

GB_REPO_ROOT="${GB_REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
GB_ARTIFACTS_DIR="${GB_ARTIFACTS_DIR:-${GB_ARTIFACTS:-${GB_REPO_ROOT}/artifacts}}"
export GB_ARTIFACTS_DIR
export GB_PORTABLE_PYTHON="/usr/bin/env -S python3"

# Back-compat aliases used by older script snippets.
export GB_ROOT="$GB_REPO_ROOT"
export GB_ARTIFACTS="$GB_ARTIFACTS_DIR"

gb_read_version() {
  python3 "${GB_REPO_ROOT}/scripts/read-version.py"
}

gb_app_id() {
  python3 "${GB_REPO_ROOT}/scripts/gen-data.py" name APP_ID
}

gb_prepare_artifacts_dir() {
  mkdir -p "${GB_ARTIFACTS_DIR}"
}

gb_source_files() {
  local top
  top="$(git -c safe.directory='*' -C "${GB_REPO_ROOT}" rev-parse --show-toplevel 2>/dev/null || true)"
  if [[ -n "${top}" && "$(cd "${top}" && pwd -P)" == "$(cd "${GB_REPO_ROOT}" && pwd -P)" ]]; then
    git -c safe.directory='*' -C "${GB_REPO_ROOT}" ls-files -z -co --exclude-standard
  else
    (cd "${GB_REPO_ROOT}" && find . \( -path ./.git -o -name __pycache__ -o -path ./artifacts \) -prune -o \
      \( -type f -o -type l \) -not -name '*.pyc' -printf '%P\0')
  fi
}

gb_copy_source_tree() {
  local dest="$1" list
  list="$(mktemp "${TMPDIR:-/tmp}/gb-src-list.XXXXXX")"
  gb_source_files | (cd "${GB_REPO_ROOT}" && while IFS= read -r -d '' f; do
    if [[ -e "${f}" || -L "${f}" ]]; then printf '%s\0' "${f}"; fi
  done) >"${list}"
  if ! tar -C "${GB_REPO_ROOT}" --null -T "${list}" -cf - | tar -C "${dest}" -xf -; then
    rm -f "${list}"
    echo "error: could not copy the source tree" >&2
    return 1
  fi
  rm -f "${list}"
}

gb_git_mount_args() {
  local common
  common="$(git -c safe.directory='*' -C "${GB_REPO_ROOT}" rev-parse --path-format=absolute --git-common-dir 2>/dev/null || true)"
  if [[ -n "${common}" && "${common}" != "${GB_REPO_ROOT}/"* ]]; then
    printf '%s\n' -v "${common}:${common}:ro"
  fi
}

gb_create_source_tarball() {
  local version="$1" dest="$2"
  local stage tmp name="geekbench7-linux-${version}"
  stage="$(mktemp -d "${TMPDIR:-/tmp}/gb-src-${version}.XXXXXX")"
  tmp="$(mktemp "${TMPDIR:-/tmp}/${name}.tar.gz.XXXXXX")"
  mkdir -p "${stage}/${name}"
  if ! gb_copy_source_tree "${stage}/${name}"; then
    rm -rf "${stage}" "${tmp}"
    return 1
  fi
  if ! tar -C "${stage}" --sort=name --owner=0 --group=0 --numeric-owner -czf "${tmp}" "${name}"; then
    rm -rf "${stage}" "${tmp}"
    return 1
  fi
  rm -rf "${stage}"
  chmod 0644 "${tmp}"
  mv "${tmp}" "${dest}"
}

gb_collect_artifacts_glob() {
  local copied=0 pattern match had_nullglob=0
  shopt -q nullglob && had_nullglob=1
  shopt -s nullglob
  for pattern in "$@"; do
    for match in ${pattern}; do
      [[ -e "${match}" ]] || continue
      # Already in the artifacts dir (same path) — count as collected.
      if [[ "$(cd "$(dirname "${match}")" && pwd -P)/$(basename "${match}")" == \
        "$(cd "${GB_ARTIFACTS_DIR}" && pwd -P)/$(basename "${match}")" ]]; then
        copied=1
        continue
      fi
      cp -a "${match}" "${GB_ARTIFACTS_DIR}/"
      copied=1
    done
  done
  ((had_nullglob)) || shopt -u nullglob
  if ((copied == 0)); then
    echo "error: no artifacts matched: $*" >&2
    return 1
  fi
}

gb_make_src_tarball() {
  local version dest
  version="$(gb_read_version)"
  dest="${GB_ARTIFACTS_DIR}/geekbench7-linux-${version}.tar.gz"
  gb_prepare_artifacts_dir
  gb_create_source_tarball "${version}" "${dest}"
  echo "${dest}"
}

gb_render_pkgbuild() {
  local version="$1" source="$2" sha256="$3"
  sed -e "s|@VERSION@|${version}|g" \
    -e "s|@SOURCE@|${source}|g" \
    -e "s|@SHA256@|${sha256}|g" \
    "${GB_REPO_ROOT}/packaging/arch/PKGBUILD.in"
}
