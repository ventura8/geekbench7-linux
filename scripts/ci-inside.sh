#!/usr/bin/env bash
# Commands run inside the CI container (mounted /src).
set -euo pipefail
cd /src
STAGE="${GB_CI_STAGE:-lint}"

run_lint() {
  python3 -m compileall -q src tests scripts
  if command -v ruff >/dev/null 2>&1; then
    ruff check src tests scripts
  fi
  python3 scripts/no-suppressions-lint.py
  python3 scripts/secret-scan.py
  python3 scripts/gen-data.py check
  python3 scripts/sonar-local.py
  if command -v shellcheck >/dev/null 2>&1; then
    # shellcheck all scripts
    mapfile -t shells < <(find scripts packaging -type f -name '*.sh' | sort)
    if ((${#shells[@]})); then
      shellcheck "${shells[@]}"
    fi
  fi
  if command -v actionlint >/dev/null 2>&1; then
    actionlint .github/workflows/*.yml
  fi
  if command -v yamllint >/dev/null 2>&1; then
    yamllint -d '{extends: default, rules: {line-length: {max: 140}}}' .github/workflows || true
  fi
  meson setup build-lint --werror -Dflavor=meson
  meson compile -C build-lint
  meson test -C build-lint --suite data
  echo "lint stage ok"
}

run_coverage() {
  mkdir -p artifacts/coverage
  python3 -m pytest tests --ignore=tests/e2e \
    --cov=geekbench7_linux \
    --cov-branch \
    --cov-report=xml:artifacts/coverage/coverage.xml \
    --cov-report=term-missing \
    -q
  python3 scripts/check-coverage.py --xml artifacts/coverage/coverage.xml --min 90
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
