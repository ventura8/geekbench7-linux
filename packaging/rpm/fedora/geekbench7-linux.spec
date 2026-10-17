%global gb_version %{?gb_version}%{!?gb_version:0.0.0}
%global app_id io.github.ventura8.Geekbench7Linux
# Pure Python/Meson wrapper — no ELF payloads worth a debuginfo package.
%global debug_package %{nil}

Name:           geekbench7-linux
Version:        %{gb_version}
Release:        1%{?dist}
Summary:        Unofficial packaging for official Geekbench 7 on Linux
License:        MIT
URL:            https://github.com/ventura8/geekbench7-linux
Source0:        %{name}-%{version}.tar.gz
ExclusiveArch:  x86_64 aarch64 riscv64
BuildRequires:  meson ninja-build python3 desktop-file-utils appstream
Requires:       python3
Requires:       (curl or wget)

%description
geekbench7-linux downloads and launches the official, unmodified Geekbench 7
Linux build from Primate Labs' CDN. Packages never embed Geekbench binaries.

Geekbench is made by Primate Labs (founder John Poole). This package is not
affiliated with Primate Labs. Please buy a license at
https://www.primatelabs.com/store/v7/ if you find Geekbench useful.

# No scriptlets: packages ship code only; per-user state is created at first run.

%prep
%autosetup -n %{name}-%{version}

%build
%meson -Dflavor=rpm -Dpython=/usr/bin/python3 -Dgeekbench_alias=true
%meson_build

%install
%meson_install

%check
%meson_test
desktop-file-validate %{buildroot}%{_datadir}/applications/%{app_id}.desktop
appstreamcli validate --no-net %{buildroot}%{_datadir}/metainfo/%{app_id}.metainfo.xml

%files
%license LICENSE
%doc README.md docs/CREDITS.md
%{_bindir}/geekbench7-linux
%{_bindir}/geekbench7
%{_datadir}/geekbench7-linux/
%{_datadir}/applications/%{app_id}.desktop
%{_datadir}/metainfo/%{app_id}.metainfo.xml
%{_datadir}/icons/hicolor/scalable/apps/%{app_id}.svg
%{_datadir}/icons/hicolor/scalable/apps/%{app_id}-symbolic.svg
%{_mandir}/man1/geekbench7-linux.1*
%{_datadir}/bash-completion/completions/geekbench7-linux
%{_datadir}/bash-completion/completions/geekbench7
%{_datadir}/zsh/site-functions/_geekbench7-linux
%{_datadir}/fish/vendor_completions.d/geekbench7-linux.fish

%changelog
* Sat Oct 17 2026 Sergiu Alexandrescu <alexandrescu.sergiu@gmail.com> - 1.0.0-1
- First stable release with SonarQube coverage gate
