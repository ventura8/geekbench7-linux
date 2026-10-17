# Compatibility

Results are filled **only from evidence** on real hosts. Never invent rows.

## Hardware QA matrix

| Host | Arch | Distro | Geekbench / wrapper | Result | Date |
|------|------|--------|---------------------|--------|------|
| sergiu-ZenBook | x86_64 | Ubuntu 26.10 | wrapper 0.1.0 | pass | 2026-10-16 |
| _(NUC)_ | | | | _pending — run scripts/qa/hardware-smoke.sh on the NUC_ | |

Run `./scripts/qa/hardware-smoke.sh` on each host and paste the snippet here.

## Package formats

| Format | Arch | Notes |
|--------|------|-------|
| deb | amd64, arm64 | PPA optional |
| rpm (Fedora) | x86_64, aarch64 | |
| rpm (openSUSE) | x86_64, aarch64 | |
| Arch | x86_64, aarch64 | PKGBUILD |
| AppImage | x86_64, aarch64 | zsync when appimagetool present |
| Flatpak | x86_64, aarch64 | |
| snap | amd64, arm64 | classic |
| tarball | both | `install.sh` |
