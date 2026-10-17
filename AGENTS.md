# Geekbench 7 for Linux (unofficial) — agent guidelines

## What this is

Unofficial convenience packaging that downloads and launches the **official,
unmodified** Geekbench 7 Linux build from Primate Labs' CDN. We ship only our
wrapper code.

Geekbench is made by **Primate Labs** (founder **John Poole**). Thank them;
never claim we made Geekbench.

## Hard rules

1. **Never redistribute, mirror, patch or decompile Geekbench binaries** — not
   in git, packages, Docker images, CI caches or artifacts.
2. **Download only from `https://cdn.geekbench.com/`**, URL built locally from
   the manifest template (amd64: `Linux.tar.gz`, arm64: `LinuxARMPreview.tar.gz`,
   riscv64: `LinuxRISCVPreview.tar.gz` — ARM/RISC-V from
   https://www.geekbench.com/preview/).
3. **HTTPS host allowlist** from the runtime manifest; refuse off-allowlist redirects.
4. **No maintainer scripts** that touch `$HOME` or run Geekbench.
5. **Credits and disclaimer stay intact** (`credits.py`, README, CREDITS.md,
   about, consent, metainfo, desktop Comment). Tests fail if stripped.
6. **No lint suppressions** (`noqa`, `type: ignore`, `pragma: no cover`,
   shellcheck disable, pytest skip/xfail as suppression, lintian overrides, …).
7. **Python 3.10+, stdlib only** for the CLI (pytest is the only test dependency).
8. **Gated E2E / real CDN tests run only in containers** (`GB_E2E*`); never bare
   on the host. Hardware QA on this machine and the NUC still uses containers.
9. **Never push, tag or publish** without an explicit maintainer request.

## Layout

See `docs/architecture/README.md`. Version SSoT: `VERSION`.
