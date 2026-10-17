#!/usr/bin/env bash
# Run SonarQube Cloud analysis for geekbench7-linux.
#
# Usage:
#   ./scripts/ci-sonar.sh                # validate token, then scan
#   ./scripts/ci-sonar.sh --check-token  # only validate the token
#
# Required: SONAR_TOKEN (env or .sonar-token at repo root).
# Optional: GB_SONAR_COVERAGE=1 to regenerate coverage + gate before upload.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCANNER_IMAGE="${GB_SONAR_IMAGE:-sonarsource/sonar-scanner-cli:12.2.0.4256_8.1.0}"
SONAR_HOST="https://sonarcloud.io"
COVERAGE_XML="${ROOT}/artifacts/coverage/coverage.xml"

cd "${ROOT}"

load_token() {
	SONAR_TOKEN="$(printf '%s' "${SONAR_TOKEN:-}" | tr -d '[:space:]')"
	if [[ -z "${SONAR_TOKEN}" && -f "${ROOT}/.sonar-token" ]]; then
		SONAR_TOKEN="$(tr -d '[:space:]' <"${ROOT}/.sonar-token")"
		export SONAR_TOKEN
		echo "==> SONAR_TOKEN loaded from .sonar-token"
	fi
	export SONAR_TOKEN
	if [[ -z "${SONAR_TOKEN}" ]]; then
		echo "error: SONAR_TOKEN is not set." >&2
		echo "       Create a token at ${SONAR_HOST}/account/security and either" >&2
		echo "       'export SONAR_TOKEN=...' or write it to ${ROOT}/.sonar-token" >&2
		exit 2
	fi
}

check_token() {
	local answer
	if ! answer="$(printf 'header = "Authorization: Bearer %s"\n' "${SONAR_TOKEN}" |
		curl --silent --show-error --fail --max-time 20 -K - "${SONAR_HOST}/api/authentication/validate" 2>&1)"; then
		echo "warning: could not reach ${SONAR_HOST} to validate SONAR_TOKEN (${answer}); continuing." >&2
		return 0
	fi
	if [[ "${answer}" == *'"valid":true'* ]]; then
		echo "==> SONAR_TOKEN is valid"
		return 0
	fi
	echo "error: SONAR_TOKEN is invalid or expired. Update .sonar-token / SONAR_TOKEN secret." >&2
	exit 1
}

ensure_coverage() {
	if [[ "${GB_SONAR_COVERAGE:-0}" == "1" || ! -f "${COVERAGE_XML}" ]]; then
		echo "==> generating coverage report"
		mkdir -p "${ROOT}/artifacts/coverage"
		if [[ -x "${ROOT}/.venv/bin/python" ]]; then
			PY="${ROOT}/.venv/bin/python"
		else
			PY=python3
		fi
		PYTHONPATH=src "${PY}" -m pytest tests --ignore=tests/e2e \
			--cov=geekbench7_linux --cov-branch \
			--cov-report=xml:"${COVERAGE_XML}" -q
	fi
	python3 "${ROOT}/scripts/check-coverage.py" --xml "${COVERAGE_XML}" --min 90
}

run_scan() {
	local version branch
	version="$(python3 "${ROOT}/scripts/read-version.py")"
	branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo main)"
	local args=(
		-Dsonar.projectVersion="${version}"
		-Dsonar.projectBaseDir=/usr/src
	)
	if [[ "${branch}" != "main" && "${branch}" != "HEAD" ]]; then
		args+=(-Dsonar.branch.name="${branch}")
	fi
	echo "==> SonarQube scan (image ${SCANNER_IMAGE}, version ${version})"
	docker run --rm \
		-e SONAR_TOKEN \
		-e SONAR_HOST_URL="${SONAR_HOST}" \
		-v "${ROOT}:/usr/src" \
		-w /usr/src \
		"${SCANNER_IMAGE}" \
		"${args[@]}"
}

load_token
if [[ "${1:-}" == "--check-token" ]]; then
	check_token
	exit 0
fi
check_token
ensure_coverage
# Prefer the GitHub Action in CI; this script is the local / fallback scanner.
if [[ -n "${GITHUB_ACTIONS:-}" && "${GB_SONAR_FORCE_DOCKER:-0}" != "1" ]]; then
	echo "==> GITHUB_ACTIONS set: coverage gated; upload via sonarqube-scan-action"
	exit 0
fi
run_scan
