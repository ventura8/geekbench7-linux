#!/usr/bin/env bash
# Local mirror of the check.yml pipeline (lint + coverage unit tests).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
GB_CI_STAGE=lint ./scripts/ci-docker.sh
GB_CI_STAGE=coverage ./scripts/ci-docker.sh
python3 scripts/gen-scenarios-doc.py check
echo "ci-pipeline: ok"
