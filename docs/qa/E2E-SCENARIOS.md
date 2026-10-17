# E2E scenarios

Generated from `tests/e2e/scenarios.json`. Do not invent rows.

| ID | Title | Gate |
|----|-------|------|
| E1 | First-run setup downloads correct arch tarball | `GB_E2E_GEEKBENCH=1` |
| E2 | Update refreshes pinned Geekbench version | `GB_E2E_GEEKBENCH=1` |
| E3 | Passthrough args reach official binary | `GB_E2E_GEEKBENCH=1` |
| E4 | Uninstall clears XDG Geekbench state only | `GB_E2E_SMOKE=1` |
| E5 | Doctor reports arch paths and hash | `GB_E2E_SMOKE=1` |
| E6 | Package smoke has wrapper and no embedded Geekbench | `GB_E2E_SMOKE=1` |
| E7 | N-1 to N wrapper upgrade keeps user Geekbench install | `GB_E2E_SMOKE=1` |
