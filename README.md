# Geekbench 7 for Linux (unofficial)

[![CI](https://github.com/ventura8/geekbench7-linux/actions/workflows/check.yml/badge.svg)](https://github.com/ventura8/geekbench7-linux/actions/workflows/check.yml)
[![Release](https://img.shields.io/github/v/release/ventura8/geekbench7-linux)](https://github.com/ventura8/geekbench7-linux/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/ventura8/geekbench7-linux/total)](https://github.com/ventura8/geekbench7-linux/releases)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=ventura8_geekbench7-linux&metric=coverage)](https://sonarcloud.io/summary/new_code?id=ventura8_geekbench7-linux)
[![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=ventura8_geekbench7-linux&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=ventura8_geekbench7-linux)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Install, update, and launch the **official Geekbench 7** Linux build — without
redistributing it.

## Credits

**Geekbench** is made by **[Primate Labs](https://www.primatelabs.com)**
(founder **John Poole**). Thank you for Geekbench.

This project is **not affiliated with, endorsed by, or supported by** Primate Labs.
Please [buy a Geekbench license](https://www.primatelabs.com/store/v7/) if you find it useful.

| | |
|--|--|
| Wrapper issues | https://github.com/ventura8/geekbench7-linux/issues |
| Geekbench itself | https://www.geekbench.com/ |
| Buy / unlock | https://www.primatelabs.com/store/v7/ |

## What it does

- Ships two entry points:
  - **`geekbench7`** — default: run official Geekbench (pass its flags through)
  - **`geekbench7-linux`** — wrapper only (`setup`, `update`, `doctor`, …)
- On first use, downloads the official tarball from `cdn.geekbench.com` into your
  XDG data directory and verifies size + sha256.
- Supports **amd64**, **arm64**, and **riscv64** (ARM/RISC-V official preview
  builds from https://www.geekbench.com/preview/).

Geekbench on Linux has no in-app auto-updater. Your package manager (or a new
release tarball) updates the **wrapper**; `geekbench7-linux update` refreshes the
**Geekbench binary** from Primate Labs' CDN.

## One-line install

```bash
curl -fsSL https://raw.githubusercontent.com/ventura8/geekbench7-linux/main/scripts/bootstrap-install.sh | bash
```

Installs under `~/.local` by default (`PREFIX` overrides). Then:

```bash
geekbench7-linux setup --accept-eula
geekbench7
```

## Install the wrapper (other options)

None of these ship Geekbench itself — that downloads on first use.

### Debian / Ubuntu (`.deb` from the release)

```bash
# download geekbench7-linux_*_amd64.deb (or arm64 / riscv64) from:
# https://github.com/ventura8/geekbench7-linux/releases/latest
sudo apt install ./geekbench7-linux_*_amd64.deb
```

### Release tarball

```bash
# unpack geekbench7-linux-VERSION-{x86_64,aarch64,riscv64}.tar.gz from the release
./install.sh
# PREFIX=$HOME/.local by default
```

### From this source tree

```bash
./install.sh
# or: meson setup build --prefix="$HOME/.local" && meson install -C build
```

Ensure `~/.local/bin` is on your `PATH` if you used the default prefix.

Other formats (RPM, Arch `.pkg.tar.zst`, AppImage, Flatpak, snap) are published on
the [GitHub Releases](https://github.com/ventura8/geekbench7-linux/releases) page
when those packaging cells succeed — use your distro’s usual local-install flow
for those artifacts.

## First-time setup

```bash
geekbench7-linux setup --accept-eula
geekbench7-linux doctor
geekbench7-linux about
```

Or via the benchmark entry point:

```bash
geekbench7 wrapper setup --accept-eula
geekbench7 wrapper doctor
```

`--accept-eula` records consent for this unofficial wrapper **and** accepts that
Geekbench’s own terms apply to the downloaded binary.

## Run benchmarks (`geekbench7`)

`geekbench7` is the default way to run Geekbench. Arguments are passed through
to the official binary.

```bash
# CPU benchmark (Geekbench default when no options are given)
geekbench7

# system info
geekbench7 --sysinfo

# GPU (API: CUDA, OpenCL, or Vulkan — OpenCL is Geekbench’s default)
geekbench7 --gpu CUDA
geekbench7 --gpu OpenCL
geekbench7 --gpu Vulkan

# list GPU platforms / devices, then pick IDs
geekbench7 --gpu-list
geekbench7 --gpu CUDA --gpu-platform-id 0 --gpu-device-id 0

# unlock with a purchased license (EMAIL and KEY from Primate Labs)
# Warning: keys on the command line can land in shell history and process lists.
geekbench7 --unlock 'you@example.com' 'YOUR-KEY'

# first run + accept consent in one step
geekbench7 --accept-eula

# Geekbench’s own help (after the separator)
geekbench7 -- --help
```

`geekbench7 -h` shows a short wrapper tip (`wrapper` / `geekbench7-linux`). You can still
insert an explicit `--` before Geekbench options:

```bash
geekbench7 -- --gpu CUDA
```

## Wrapper commands (`geekbench7-linux`)

`geekbench7-linux` only manages the install — it does **not** run benchmarks.

| Command | Purpose |
|---------|---------|
| `setup --accept-eula` | Download and extract Geekbench 7 |
| `setup --arch amd64\|arm64\|riscv64` | Override detected architecture |
| `update` | Re-download the pinned CDN build |
| `doctor` | Paths, arch, and install status |
| `about` | Credits and disclaimer |
| `version` | Wrapper version |
| `uninstall [--yes]` | Remove per-user Geekbench data (keeps the package) |
| `desktop install\|remove` | Per-user `.desktop` menu entry |

Same commands via `geekbench7 wrapper …`:

```bash
geekbench7-linux --help
geekbench7-linux doctor
geekbench7-linux update
geekbench7-linux uninstall --yes
geekbench7-linux desktop install

geekbench7 wrapper version
geekbench7 wrapper about
```

Global wrapper flags: `--json`, `--allow-root`, `-v`.

## Where files live

| What | Typical location |
|------|------------------|
| Wrapper (user install) | `~/.local/bin/geekbench7`, `~/.local/bin/geekbench7-linux` |
| Geekbench extract | `~/.local/share/geekbench7-linux/geekbench/` |
| Cache / downloads | under XDG cache for this app |
| Config / consent | under XDG config for this app |

`geekbench7-linux doctor` prints the resolved paths for your machine.

## Troubleshooting

**`unrecognized arguments: --gpu` on `geekbench7-linux`**  
Use `geekbench7 --gpu CUDA`. `geekbench7-linux` is wrapper-only (no benchmark
passthrough).

**`unrecognized option '--gpu [cuda]'`**  
Do not quote the whole flag, and do not type the help brackets. Use
`--gpu CUDA` (uppercase API names as in Geekbench’s help).

**Need a license**  
Buy at https://www.primatelabs.com/store/v7/ then
`geekbench7 --unlock 'EMAIL' 'KEY'`. Prefer a private shell session; keys can
appear in history and `ps` output.

**Wrong architecture**  
`geekbench7-linux setup --accept-eula --arch arm64` (or `amd64` / `riscv64`).

## Development

```bash
meson setup build && meson compile -C build
PYTHONPATH=src python3 -m pytest tests -q
GB_CI_STAGE=lint ./scripts/ci-docker.sh
GB_CI_STAGE=coverage ./scripts/ci-docker.sh
./scripts/qa/hardware-smoke.sh   # this machine / NUC (containerized)
```

Gated real-CDN E2E runs only in containers (`./scripts/e2e-docker.sh`).

See [AGENTS.md](AGENTS.md), [docs/CREDITS.md](docs/CREDITS.md),
[docs/COMPATIBILITY.md](docs/COMPATIBILITY.md), and
[docs/architecture/README.md](docs/architecture/README.md).

## License

MIT for the wrapper. Geekbench remains proprietary to Primate Labs.
