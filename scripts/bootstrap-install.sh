#!/usr/bin/env bash
# One-line installer: download the latest relocatable release tarball and install.
#
#   curl -fsSL https://raw.githubusercontent.com/ventura8/geekbench7-linux/main/scripts/bootstrap-install.sh | bash
#
# Env: PREFIX (default ~/.local), GB_VERSION (default: latest GitHub release tag without v).
set -euo pipefail

REPO="${GB_REPO:-ventura8/geekbench7-linux}"
PREFIX="${PREFIX:-$HOME/.local}"
API="https://api.github.com/repos/${REPO}/releases/latest"

need_cmd() {
	command -v "$1" >/dev/null 2>&1 || {
		echo "error: need '$1' on PATH" >&2
		exit 2
	}
}

need_cmd curl
need_cmd tar
need_cmd uname

arch="$(uname -m)"
case "${arch}" in
x86_64 | amd64) asset_arch=x86_64 ;;
aarch64 | arm64) asset_arch=aarch64 ;;
riscv64) asset_arch=riscv64 ;;
*)
	echo "error: unsupported machine arch '${arch}'" >&2
	exit 2
	;;
esac

if [[ -n "${GB_VERSION:-}" ]]; then
	version="${GB_VERSION#v}"
	tag="v${version}"
	base="https://github.com/${REPO}/releases/download/${tag}"
else
	json="$(curl -fsSL "${API}")"
	tag="$(printf '%s\n' "${json}" | sed -n 's/.*"tag_name":[[:space:]]*"\([^"]*\)".*/\1/p' | head -n1)"
	version="${tag#v}"
	if [[ -z "${version}" ]]; then
		echo "error: could not resolve latest release from ${API}" >&2
		exit 1
	fi
	base="https://github.com/${REPO}/releases/download/${tag}"
fi

asset="geekbench7-linux-${version}-${asset_arch}.tar.gz"
url="${base}/${asset}"
workdir="$(mktemp -d "${TMPDIR:-/tmp}/gb7-install.XXXXXX")"
cleanup() { rm -rf "${workdir}"; }
trap cleanup EXIT

echo "==> downloading ${url}"
curl -fsSL -o "${workdir}/${asset}" "${url}"
tar -xzf "${workdir}/${asset}" -C "${workdir}"
# Tarball contains a single top-level directory.
root="$(find "${workdir}" -mindepth 1 -maxdepth 1 -type d | head -n1)"
if [[ -z "${root}" || ! -x "${root}/install.sh" ]]; then
	echo "error: unexpected tarball layout in ${asset}" >&2
	exit 1
fi

echo "==> installing to ${PREFIX}"
PREFIX="${PREFIX}" "${root}/install.sh"
echo "==> done. Ensure ${PREFIX}/bin is on your PATH, then:"
echo "    geekbench7-linux setup --accept-eula"
echo "    geekbench7"
