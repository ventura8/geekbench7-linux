# bash completion for geekbench7-linux / geekbench7
_geekbench7_linux() {
  local cur
  COMPREPLY=()
  cur="${COMP_WORDS[COMP_CWORD]}"
  if [[ ${COMP_CWORD} -eq 1 ]]; then
    COMPREPLY=($(compgen -W "setup update doctor about uninstall desktop version -h --help -V --version" -- "${cur}"))
    return 0
  fi
  case "${COMP_WORDS[1]}" in
    desktop)
      COMPREPLY=($(compgen -W "install remove" -- "${cur}"))
      ;;
    setup)
      COMPREPLY=($(compgen -W "--accept-eula --arch --json --allow-root" -- "${cur}"))
      ;;
    *)
      COMPREPLY=()
      ;;
  esac
}

_geekbench7() {
  local cur
  COMPREPLY=()
  cur="${COMP_WORDS[COMP_CWORD]}"
  if [[ ${COMP_CWORD} -eq 1 ]]; then
    COMPREPLY=($(compgen -W "wrapper --accept-eula --sysinfo --gpu --gpu-list --unlock -h --help -V --version" -- "${cur}"))
    return 0
  fi
  if [[ "${COMP_WORDS[1]}" == "wrapper" ]]; then
    if [[ ${COMP_CWORD} -eq 2 ]]; then
      COMPREPLY=($(compgen -W "setup update doctor about uninstall desktop version" -- "${cur}"))
      return 0
    fi
    case "${COMP_WORDS[2]}" in
      desktop)
        COMPREPLY=($(compgen -W "install remove" -- "${cur}"))
        ;;
      setup)
        COMPREPLY=($(compgen -W "--accept-eula --arch --json --allow-root" -- "${cur}"))
        ;;
      *)
        COMPREPLY=()
        ;;
    esac
  fi
}

complete -F _geekbench7_linux geekbench7-linux
complete -F _geekbench7 geekbench7
