#!/usr/bin/env bash
# Install geekbench7-linux from a source tree or a relocatable release tarball.
set -euo pipefail
PREFIX="${PREFIX:-$HOME/.local}"
ROOT="$(cd "$(dirname "$0")" && pwd)"

if [[ -x "${ROOT}/bin/geekbench7-linux" ]]; then
  # Relocatable prefix layout (geekbench7-linux-VERSION/{bin,share,...}).
  mkdir -p "${PREFIX}"
  cp -a "${ROOT}/bin" "${ROOT}/share" "${PREFIX}/"
  if [[ -d "${ROOT}/lib" ]]; then
    cp -a "${ROOT}/lib" "${PREFIX}/"
  fi
  echo "Installed geekbench7-linux to ${PREFIX} (relocatable layout)"
else
  meson setup "${ROOT}/build-user" --prefix="${PREFIX}" -Dflavor=tarball \
    -Dpython="/usr/bin/env -S python3"
  meson install -C "${ROOT}/build-user"
  echo "Installed geekbench7-linux to ${PREFIX}"
fi
echo "Geekbench itself is downloaded on first run from cdn.geekbench.com"
echo "Thank you to Primate Labs and John Poole for Geekbench."
