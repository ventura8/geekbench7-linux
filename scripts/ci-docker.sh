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
docker run --rm \
  -e HOME=/tmp/gb-home \
  -e GB_CI_STAGE="$STAGE" \
  -v "$ROOT:/src:ro" \
  -w /src \
  "$IMAGE_TAG" \
  /src/scripts/ci-inside.sh
