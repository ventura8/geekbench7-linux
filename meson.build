# meson.build - Geekbench 7 for Linux (unofficial).
#
# Installs:
#   <bindir>/geekbench7-linux [, geekbench7 symlink]
#   <datadir>/geekbench7-linux/geekbench7_linux/
#   desktop / metainfo / icons / man / completions
#
# Packages never embed Geekbench binaries; the wrapper downloads them per-user.

project(
  'geekbench7-linux',
  version: run_command('python3', 'scripts/read-version.py', check: true).stdout().strip(),
  license: 'MIT',
  meson_version: '>= 0.61.0',
)

gb_python = find_program('python3')
gb_gen = files('scripts/gen-data.py')
gb_shebang = get_option('python')
if gb_shebang == ''
  gb_shebang = gb_python.full_path()
endif
gb_app_id = run_command(gb_python, gb_gen, 'name', 'APP_ID', check: true).stdout().strip()

gb_prefix = get_option('prefix')
gb_bindir = get_option('bindir')
gb_datadir = get_option('datadir')
gb_pkgdatadir = gb_datadir / 'geekbench7-linux'

gb_launcher_conf = configuration_data()
gb_launcher_conf.set('PYTHON', gb_shebang)

configure_file(
  input: 'bin/geekbench7-linux.in',
  output: 'geekbench7-linux',
  configuration: gb_launcher_conf,
  install: true,
  install_dir: gb_bindir,
  install_mode: 'rwxr-xr-x',
)
if get_option('geekbench_alias')
  install_symlink('geekbench7', pointing_to: 'geekbench7-linux', install_dir: gb_bindir)
endif

install_subdir(
  'src/geekbench7_linux',
  install_dir: gb_pkgdatadir,
  exclude_directories: ['__pycache__', '.ruff_cache', 'commands/__pycache__', 'data/__pycache__'],
  exclude_files: ['_build.py'],
)

custom_target(
  'gb-build-info',
  output: '_build.py',
  command: [gb_python, gb_gen, 'build-info', meson.project_version(), get_option('flavor'), '@OUTPUT@'],
  install: true,
  install_dir: gb_pkgdatadir / 'geekbench7_linux',
)

if get_option('desktop')
  gb_desktop_file = custom_target(
    'gb-desktop',
    output: gb_app_id + '.desktop',
    command: [gb_python, gb_gen, 'desktop', '@OUTPUT@'],
    depend_files: files(
      'src/geekbench7_linux/data/templates/io.github.ventura8.Geekbench7Linux.desktop.in',
      'src/geekbench7_linux/credits.py',
      'src/geekbench7_linux/__init__.py',
    ),
    install: true,
    install_dir: gb_datadir / 'applications',
  )
  gb_metainfo_file = custom_target(
    'gb-metainfo',
    output: gb_app_id + '.metainfo.xml',
    command: [gb_python, gb_gen, 'metainfo', '@OUTPUT@'],
    depend_files: files(
      'data/' + gb_app_id + '.metainfo.xml.in',
      'src/geekbench7_linux/credits.py',
      'src/geekbench7_linux/__init__.py',
    ),
    install: true,
    install_dir: gb_datadir / 'metainfo',
  )
  install_subdir('data/icons/hicolor', install_dir: gb_datadir / 'icons')
endif

install_man('data/man/geekbench7-linux.1')

gb_bash_dir = gb_datadir / 'bash-completion' / 'completions'
install_data('data/completions/geekbench7-linux.bash', rename: 'geekbench7-linux', install_dir: gb_bash_dir)
install_data('data/completions/_geekbench7-linux', install_dir: gb_datadir / 'zsh' / 'site-functions')
install_data('data/completions/geekbench7-linux.fish', install_dir: gb_datadir / 'fish' / 'vendor_completions.d')
if get_option('geekbench_alias')
  install_symlink('geekbench7', pointing_to: 'geekbench7-linux', install_dir: gb_bash_dir)
endif

test('gen-data-check', gb_python, args: [gb_gen, 'check'], suite: 'data')
if get_option('desktop')
  gb_dfv = find_program('desktop-file-validate', required: false)
  if gb_dfv.found()
    test('desktop-file-validate', gb_dfv, args: [gb_desktop_file], suite: 'data')
  endif
  gb_appstreamcli = find_program('appstreamcli', required: false)
  if gb_appstreamcli.found()
    test('appstreamcli-validate', gb_appstreamcli, args: ['validate', '--no-net', gb_metainfo_file], suite: 'data')
  endif
endif
