#!/usr/bin/env bash
# Shared helpers for release scripts.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export GB_ROOT="$ROOT"
export GB_VERSION
GB_VERSION="$(python3 "$ROOT/scripts/read-version.py")"
export GB_ARTIFACTS="${GB_ARTIFACTS:-$ROOT/artifacts}"
mkdir -p "$GB_ARTIFACTS"

gb_make_src_tarball() {
  local dest="$GB_ARTIFACTS/geekbench7-linux-${GB_VERSION}.tar.gz"
  tar -C "$ROOT" --exclude=.git --exclude=artifacts --exclude=build --exclude='build-*' \
    -czf "$dest" .
  echo "$dest"
}
