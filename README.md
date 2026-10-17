# Geekbench 7 for Linux (unofficial)

Install, update and launch the **official Geekbench 7** Linux build — without
redistributing it.

## Credits

**Geekbench** is made by **[Primate Labs](https://www.primatelabs.com)**
(founder **John Poole**). Thank you for Geekbench.

This project is **not affiliated with, endorsed by, or supported by** Primate Labs.
Please [buy a Geekbench license](https://www.geekbench.com/buy/) if you find it useful.

Wrapper issues: https://github.com/ventura8/geekbench7-linux/issues  
Geekbench itself: contact Primate Labs via https://www.geekbench.com/

## What it does

- Packages a small wrapper (`geekbench7-linux`) as `.deb`, `.rpm`, Arch, AppImage,
  Flatpak, snap or tarball.
- On first run (or `update`), downloads the official tarball from
  `cdn.geekbench.com` into your XDG data directory and verifies it.
- Supports **amd64** and **arm64** (ARM preview builds).

Geekbench on Linux has no in-app auto-updater. **Your package manager updates
the wrapper**; **`geekbench7-linux update`** (and our upstream-watch pins)
refresh the Geekbench binary from Primate Labs' CDN.

## Quick start

```bash
# from a release tarball
./install.sh
geekbench7-linux setup --accept-eula
geekbench7-linux run
# or: geekbench7
```

## Commands

| Command | Purpose |
|---------|---------|
| `setup --accept-eula` | Download and extract Geekbench 7 |
| `run` | Exec official `geekbench7` (passthrough args) |
| `update` | Refresh the pinned version from the CDN |
| `doctor` | Paths, arch, status |
| `about` | Credits and disclaimer |
| `uninstall` | Remove per-user Geekbench state |
| `desktop install` | Per-user menu entry |

## Development

```bash
meson setup build && meson compile -C build
python3 -m pytest tests -q
GB_CI_STAGE=lint ./scripts/ci-docker.sh
./scripts/qa/hardware-smoke.sh   # this machine / NUC (containerized)
```

See [AGENTS.md](AGENTS.md), [docs/CREDITS.md](docs/CREDITS.md),
[docs/COMPATIBILITY.md](docs/COMPATIBILITY.md).

## License

MIT for the wrapper. Geekbench remains proprietary to Primate Labs.
