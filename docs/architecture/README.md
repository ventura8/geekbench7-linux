# Architecture

```text
package (deb/rpm/…)  →  geekbench7-linux CLI  →  CDN download  →  ~/.local/share/…/geekbench/
                                                              →  exec geekbench7
```

- **Wrapper updates:** package manager / AppImage zsync / `install.sh`
- **Geekbench updates:** `geekbench7-linux update` + `upstream-watch` pinning
- **Never** ship Geekbench binaries in packages or git
