complete -c geekbench7-linux -f
complete -c geekbench7-linux -n __fish_use_subcommand -a setup -d 'Download Geekbench 7'
complete -c geekbench7-linux -n __fish_use_subcommand -a update -d 'Update Geekbench from CDN'
complete -c geekbench7-linux -n __fish_use_subcommand -a doctor -d 'Health check'
complete -c geekbench7-linux -n __fish_use_subcommand -a about -d 'Credits and disclaimer'
complete -c geekbench7-linux -n __fish_use_subcommand -a uninstall -d 'Remove per-user state'
complete -c geekbench7-linux -n __fish_use_subcommand -a desktop -d 'Menu entry'
complete -c geekbench7-linux -n __fish_use_subcommand -a version -d 'Wrapper version'
complete -c geekbench7-linux -n '__fish_seen_subcommand_from desktop' -a 'install remove'
