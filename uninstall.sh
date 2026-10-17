#!/usr/bin/env bash
# Remove a user-prefix install (does not remove per-user Geekbench downloads).
set -euo pipefail
PREFIX="${PREFIX:-$HOME/.local}"
rm -f "$PREFIX/bin/geekbench7-linux" "$PREFIX/bin/geekbench7"
rm -rf "$PREFIX/share/geekbench7-linux"
rm -f "$PREFIX/share/applications/io.github.ventura8.Geekbench7Linux.desktop"
rm -f "$PREFIX/share/metainfo/io.github.ventura8.Geekbench7Linux.metainfo.xml"
echo "Removed wrapper from $PREFIX (Geekbench extract under ~/.local/share/geekbench7-linux left intact;"
echo "run: geekbench7-linux uninstall --yes  to remove it)"
