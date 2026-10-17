#!/usr/bin/env bash
# User-prefix install of geekbench7-linux from a source / release tarball.
set -euo pipefail
PREFIX="${PREFIX:-$HOME/.local}"
ROOT="$(cd "$(dirname "$0")" && pwd)"
meson setup "$ROOT/build-user" --prefix="$PREFIX" -Dflavor=tarball -Dpython="/usr/bin/env -S python3"
meson install -C "$ROOT/build-user"
echo "Installed geekbench7-linux to $PREFIX"
echo "Geekbench itself is downloaded on first run from cdn.geekbench.com"
echo "Thank you to Primate Labs and John Poole for Geekbench."
