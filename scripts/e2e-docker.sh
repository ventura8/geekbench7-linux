#!/usr/bin/env bash
# Run E2E tests only inside a container (as a non-root user).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MODE="${1:-smoke}"
IMAGE="geekbench7-linux-e2e:local"
cd "$ROOT"
docker build -f docker/Dockerfile.e2e -t "$IMAGE" .

SCRATCH="$(mktemp -d /tmp/gb-e2e.XXXXXX)"
mkdir -p "$SCRATCH/home" "$SCRATCH/pytest-cache"
cleanup() { rm -rf "$SCRATCH"; }
trap cleanup EXIT

ENV_ARGS=(
  -e HOME=/scratch/home
  -e GB_E2E=1
  -e GB_E2E_SCRATCH=/scratch
  -e PYTEST_ADDOPTS="-o cache_dir=/scratch/pytest-cache"
)
PYTEST_ARGS=(tests/e2e -q)
if [[ "$MODE" == "real" ]]; then
  ENV_ARGS+=(-e GB_E2E_GEEKBENCH=1)
  PYTEST_ARGS+=(-m "not slow")
else
  ENV_ARGS+=(-e GB_E2E_SMOKE=1)
fi

UID_GID="$(id -u):$(id -g)"
docker run --rm \
  --user "$UID_GID" \
  "${ENV_ARGS[@]}" \
  -v "$ROOT:/src:ro" \
  -v "$SCRATCH:/scratch" \
  -w /src \
  "$IMAGE" \
  python3 -m pytest "${PYTEST_ARGS[@]}"
