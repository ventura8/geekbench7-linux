# Architecture

```text
package (deb/rpm/…)  →  geekbench7 / geekbench7-linux  →  CDN download  →  ~/.local/share/…/geekbench/
                                                                  →  exec official geekbench7
```

- **Benchmark entry:** `geekbench7` (passthrough); management: `geekbench7-linux` or `geekbench7 wrapper …`
- **Wrapper updates:** package manager / AppImage zsync / `install.sh`
- **Geekbench updates:** `geekbench7-linux update` + `upstream-watch` pinning
- **Never** ship Geekbench binaries in packages or git
