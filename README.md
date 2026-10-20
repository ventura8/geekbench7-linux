# Geekbench 7 for Linux (unofficial)

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

- Ships a small wrapper (`geekbench7-linux`, plus a `geekbench7` alias) as
  `.deb`, `.rpm`, Arch, AppImage, Flatpak, snap, or tarball.
- On first run (or `setup` / `update`), downloads the official tarball from
  `cdn.geekbench.com` into your XDG data directory and verifies size + sha256.
- Supports **amd64**, **arm64**, and **riscv64** (ARM/RISC-V official preview
  builds from https://www.geekbench.com/preview/).

Geekbench on Linux has no in-app auto-updater. **Your package manager updates
the wrapper**; **`geekbench7-linux update`** refreshes the Geekbench binary from
Primate Labs' CDN.

## Install the wrapper

Pick one path. None of these ship Geekbench itself — that downloads on first use.

### From a GitHub Release tarball

```bash
# after unpacking geekbench7-linux-VERSION-*.tar.gz
./install.sh
# installs under ~/.local by default (PREFIX=$HOME/.local)
```

### From packages

```bash
# Debian / Ubuntu
sudo apt install ./geekbench7-linux_*_amd64.deb

# Fedora
sudo dnf install ./geekbench7-linux-*.rpm

# Arch (from PKGBUILD / .pkg.tar.zst in the release)
sudo pacman -U ./geekbench7-linux-*.pkg.tar.zst
```

AppImage, Flatpak, and snap assets are also published on the release page when
the packaging cell succeeds.

### From this source tree

```bash
./install.sh
# or: meson setup build --prefix="$HOME/.local" && meson install -C build
```

Ensure `~/.local/bin` is on your `PATH` if you used the default prefix.

## First-time setup

```bash
geekbench7-linux setup --accept-eula
geekbench7-linux doctor          # paths, arch, install status
geekbench7-linux about           # credits + disclaimer
```

`--accept-eula` records consent for this unofficial wrapper **and** accepts that
Geekbench’s own terms apply to the downloaded binary.

## Run benchmarks

Anything after `run` is passed through to the official `geekbench7` binary.

```bash
# CPU benchmark (Geekbench default when no options are given)
geekbench7-linux run

# same via the short alias (defaults to run)
geekbench7

# system info only
geekbench7-linux run --sysinfo

# GPU benchmark (API: CUDA, OpenCL, or Vulkan — OpenCL is Geekbench’s default)
geekbench7-linux run --gpu CUDA
geekbench7-linux run --gpu OpenCL
geekbench7-linux run --gpu Vulkan

# list GPU platforms / devices, then pick IDs
geekbench7-linux run --gpu-list
geekbench7-linux run --gpu CUDA --gpu-platform-id 0 --gpu-device-id 0

# unlock with a purchased license (EMAIL and KEY from Primate Labs)
# Warning: keys on the command line can land in shell history and process lists.
geekbench7-linux run --unlock 'you@example.com' 'YOUR-KEY'

# see every flag Geekbench supports
geekbench7-linux run --help
```

You can still use an explicit separator if you prefer:

```bash
geekbench7-linux run -- --gpu CUDA
```

Global wrapper flags (`--json`, `--allow-root`, `-v`, `--accept-eula`) must
appear **before** Geekbench’s own options, or after `run` before those options:

```bash
geekbench7-linux --json doctor
geekbench7-linux run --accept-eula --gpu CUDA
```

## Command reference

| Command | Purpose |
|---------|---------|
| `setup --accept-eula` | Download and extract Geekbench 7 |
| `setup --arch amd64\|arm64\|riscv64` | Override detected architecture |
| `run [geekbench options…]` | Exec official `geekbench7` (passthrough) |
| `update` | Re-download the pinned CDN build |
| `doctor` | Paths, arch, and install status |
| `about` | Credits and disclaimer |
| `version` | Wrapper version (`VERSION` file / package) |
| `uninstall [--yes]` | Remove per-user Geekbench data (keeps the package) |
| `desktop install\|remove` | Per-user `.desktop` menu entry |

```bash
geekbench7-linux --help
geekbench7-linux run --help      # Geekbench’s own help
geekbench7-linux doctor
geekbench7-linux update
geekbench7-linux uninstall --yes
geekbench7-linux desktop install
```

## Where files live

| What | Typical location |
|------|------------------|
| Wrapper (user install) | `~/.local/bin/geekbench7-linux` |
| Geekbench extract | `~/.local/share/geekbench7-linux/geekbench/` |
| Cache / downloads | under XDG cache for this app |
| Config / consent | under XDG config for this app |

`doctor` prints the resolved paths for your machine.

## Troubleshooting

**`unrecognized arguments: --gpu`**  
Update to wrapper **≥ 1.0.1**, or use `geekbench7-linux run -- --gpu CUDA`.

**`unrecognized option '--gpu [cuda]'`**  
Do not quote the whole flag, and do not type the help brackets. Use
`--gpu CUDA` (uppercase API names as in Geekbench’s help).

**Need a license**  
Buy at https://www.primatelabs.com/store/v7/ then
`geekbench7-linux run --unlock 'EMAIL' 'KEY'`.
Prefer a private shell session; command-line keys can appear in history and
`ps` output.

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
