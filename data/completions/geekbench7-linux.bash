# bash completion for geekbench7-linux
_geekbench7_linux() {
  local cur prev
  COMPREPLY=()
  cur="${COMP_WORDS[COMP_CWORD]}"
  prev="${COMP_WORDS[COMP_CWORD - 1]}"
  if [[ ${COMP_CWORD} -eq 1 ]]; then
    COMPREPLY=($(compgen -W "setup run update doctor about uninstall desktop version -h --help -V --version" -- "${cur}"))
    return 0
  fi
  case "${COMP_WORDS[1]}" in
    desktop)
      COMPREPLY=($(compgen -W "install remove" -- "${cur}"))
      ;;
    setup | run)
      COMPREPLY=($(compgen -W "--accept-eula --json --allow-root" -- "${cur}"))
      ;;
    *)
      COMPREPLY=()
      ;;
  esac
}
complete -F _geekbench7_linux geekbench7-linux
complete -F _geekbench7_linux geekbench7
