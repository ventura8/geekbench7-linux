#!/usr/bin/env bash
# Build the snap on the host runner with snapcraft (classic).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}"
export GB_ARTIFACTS_DIR="${GB_ARTIFACTS_DIR:-${ROOT}/artifacts}"
mkdir -p "${GB_ARTIFACTS_DIR}"

if ! command -v snapcraft >/dev/null 2>&1; then
  sudo snap install snapcraft --classic
fi
# Host needs meson/ninja for --destructive-mode builds.
if ! command -v meson >/dev/null 2>&1; then
  sudo apt-get update
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y meson ninja-build python3
fi

./scripts/release-portable.sh snap
