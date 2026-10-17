# Hardware QA checklist

## This development machine

1. `cd` to the geekbench7-linux checkout.
2. `./scripts/qa/hardware-smoke.sh`
3. Paste the printed table row into `docs/COMPATIBILITY.md`.
4. Optionally run real CDN E2E: `./scripts/e2e-docker.sh real` (network + container).

## NUC

1. Sync or clone the same commit onto the NUC (SSH or local).
2. Ensure Docker (or Podman with docker CLI) is available.
3. Run `./scripts/qa/hardware-smoke.sh`.
4. Paste the result row into `docs/COMPATIBILITY.md` with the NUC hostname.

## Before a release

- [ ] Smoke pass on this machine
- [ ] Smoke pass on the NUC
- [ ] COMPATIBILITY.md updated with dates
- [ ] No Geekbench tarballs committed
