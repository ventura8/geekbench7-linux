#!/usr/bin/env bash
# Run container smoke E2E on the current host; print a COMPATIBILITY.md snippet.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HOST="$(hostname -s 2>/dev/null || hostname)"
ARCH="$(uname -m)"
DISTRO="unknown"
if [[ -f /etc/os-release ]]; then
  # shellcheck source=/dev/null
  . /etc/os-release
  DISTRO="${PRETTY_NAME:-$ID}"
fi
DATE="$(date -u +%Y-%m-%d)"
echo "Running hardware smoke on host=$HOST arch=$ARCH distro=$DISTRO"
cd "$ROOT"
if ./scripts/e2e-docker.sh smoke; then
  RESULT=pass
else
  RESULT=fail
fi
VERSION="$(python3 scripts/read-version.py)"
echo
echo "COMPATIBILITY snippet:"
echo "| $HOST | $ARCH | $DISTRO | wrapper $VERSION | $RESULT | $DATE |"
