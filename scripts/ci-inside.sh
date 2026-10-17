#!/usr/bin/env bash
# Commands run inside the CI container (mounted /src).
set -euo pipefail
# Source tree may be mounted read-only: keep bytecode off the mount.
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPYCACHEPREFIX="${PYTHONPYCACHEPREFIX:-/tmp/gb-pycache}"
mkdir -p "$PYTHONPYCACHEPREFIX"
cd /src
STAGE="${GB_CI_STAGE:-lint}"

run_lint() {
  python3 -m compileall -q src tests scripts
  if command -v ruff >/dev/null 2>&1; then
    export RUFF_CACHE_DIR="${RUFF_CACHE_DIR:-/tmp/gb-ruff-cache}"
    mkdir -p "$RUFF_CACHE_DIR"
    ruff check --no-cache src tests scripts
  fi
  python3 scripts/no-suppressions-lint.py
  python3 scripts/secret-scan.py
  python3 scripts/gen-data.py check
  python3 scripts/sonar-local.py
  if command -v shellcheck >/dev/null 2>&1; then
    # Lint every bash script under scripts/ and packaging/.
    mapfile -t shells < <(find scripts packaging -type f -name '*.sh' | sort)
    if ((${#shells[@]})); then
      # SC1091: sourced helpers are resolved via -x from the same tree.
      shellcheck -x -e SC1091 "${shells[@]}"
    fi
  fi
  if command -v actionlint >/dev/null 2>&1; then
    actionlint .github/workflows/*.yml
  fi
  if command -v yamllint >/dev/null 2>&1; then
    yamllint -d '{extends: default, rules: {line-length: {max: 140}}}' .github/workflows || true
  fi
  # Meson build dir must be writable (not on a read-only /src mount).
  BUILD_DIR="${GB_BUILD_DIR:-/tmp/gb-build-lint}"
  rm -rf "$BUILD_DIR"
  meson setup "$BUILD_DIR" --werror -Dflavor=meson
  meson compile -C "$BUILD_DIR"
  meson test -C "$BUILD_DIR" --suite data
  echo "lint stage ok"
}

run_coverage() {
  mkdir -p /tmp/gb-coverage
  # Prefer a writable report path when /src is read-only.
  COVERAGE_XML="${GB_COVERAGE_XML:-/tmp/gb-coverage/coverage.xml}"
  python3 -m pytest tests --ignore=tests/e2e \
    --cov=geekbench7_linux \
    --cov-branch \
    --cov-report=xml:"${COVERAGE_XML}" \
    --cov-report=term-missing \
    -q
  mkdir -p artifacts/coverage 2>/dev/null || true
  if [[ -d artifacts/coverage && -w artifacts ]]; then
    cp -f "${COVERAGE_XML}" artifacts/coverage/coverage.xml
    COVERAGE_XML=artifacts/coverage/coverage.xml
  fi
  python3 scripts/check-coverage.py --xml "${COVERAGE_XML}" --min 90
}

run_compat() {
  python3 -m pytest tests -q
}

case "$STAGE" in
  lint) run_lint ;;
  coverage) run_coverage ;;
  compat) run_compat ;;
  *) echo "unknown stage $STAGE" >&2; exit 2 ;;
esac
