#!/usr/bin/env bash
# Run a CI stage inside Docker. Stages: lint | coverage | compat
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STAGE="${GB_CI_STAGE:-${FL_CI_STAGE:-lint}}"
IMAGE_TAG="geekbench7-linux-ci-${STAGE}:local"

case "$STAGE" in
  lint) DOCKERFILE="docker/Dockerfile.ci.lint" ;;
  coverage) DOCKERFILE="docker/Dockerfile.ci.coverage" ;;
  compat) DOCKERFILE="docker/Dockerfile.ci.compat" ;;
  *) echo "unknown stage: $STAGE" >&2; exit 2 ;;
esac

cd "$ROOT"
docker build -f "$DOCKERFILE" -t "$IMAGE_TAG" .
# Mount repo read-only; writable scratch for caches, meson build, coverage XML.
SCRATCH="$(mktemp -d /tmp/gb-ci.XXXXXX)"
cleanup() { rm -rf "$SCRATCH" 2>/dev/null || true; }
trap cleanup EXIT
mkdir -p \
  "$SCRATCH/home" \
  "$SCRATCH/pycache" \
  "$SCRATCH/build" \
  "$SCRATCH/coverage" \
  "$SCRATCH/ruff" \
  "$SCRATCH/pytest"
# Match host UID so scratch files are removable without sudo.
HOST_UID="$(id -u)"
HOST_GID="$(id -g)"
docker run --rm \
  --user "${HOST_UID}:${HOST_GID}" \
  -e HOME=/scratch/home \
  -e GB_CI_STAGE="$STAGE" \
  -e PYTHONPYCACHEPREFIX=/scratch/pycache \
  -e PYTHONDONTWRITEBYTECODE=1 \
  -e GB_BUILD_DIR=/scratch/build \
  -e GB_COVERAGE_XML=/scratch/coverage/coverage.xml \
  -e COVERAGE_FILE=/scratch/coverage/.coverage \
  -e RUFF_CACHE_DIR=/scratch/ruff \
  -e PYTEST_ADDOPTS="-o cache_dir=/scratch/pytest" \
  -v "$ROOT:/src:ro" \
  -v "$SCRATCH:/scratch" \
  -w /src \
  "$IMAGE_TAG" \
  /src/scripts/ci-inside.sh
# Copy coverage report back for Sonar / local gates when present.
if [[ -f "$SCRATCH/coverage/coverage.xml" ]]; then
  mkdir -p "$ROOT/artifacts/coverage"
  cp -f "$SCRATCH/coverage/coverage.xml" "$ROOT/artifacts/coverage/coverage.xml"
fi
