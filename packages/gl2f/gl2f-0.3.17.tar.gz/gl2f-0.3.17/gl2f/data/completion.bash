__gl2f_complete_boards(){
  if [[ "$cur" == */* ]]; then
    local realcur=${cur##*/}
    local prefix=${cur%/*}
    case ${prefix} in
## REPLACE_PAGES_SECOND
    esac
  else
    ## REPLACE_PAGES_FIRST

    if declare -F _init_completion >/dev/null 2>&1; then
      [[ $COMPREPLY == */ ]] && compopt -o nospace # not work on mac
    fi
  fi
}

__gl2f_complete_format(){
  local realcur=$cur
  if [[ "$cur" == *:* ]]; then
    realcur=${cur##*:}
  fi

  ## REPLACE_FORMAT

  if declare -F _init_completion >/dev/null 2>&1; then
    compopt -o nospace
  fi
}

__gl2f_complete_order(){
  if [[ "$cur" == *:* ]]; then
    local realcur=${cur##*:}
    COMPREPLY=( $(compgen -W "asc desc" -- $realcur) )
  else
    COMPREPLY=( $(compgen -W "name: reservedAt:" -- $cur) )
    if declare -F _init_completion >/dev/null 2>&1; then
      compopt -o nospace
    fi
  fi
}

__gl2f_complete_list_args(){
  if [ $prev == "-f"  ] || [ $prev == "--format" ]; then
    __gl2f_complete_format
  elif [ $prev == --order ]; then
    __gl2f_complete_order
  elif [ $prev == --dump ]; then
    _filedir
  else
    __gl2f_complete_boards
  fi
}

_gl2f(){
  local cur prev words cword split
  if declare -F _init_completion >/dev/null 2>&1; then
    _init_completion -n :/ || return
  else
    COMPREPLY=()
    _get_comp_words_by_ref -n :/ cur prev words cword || return
  fi

## REPLACE_COMMAND_TREE
}

if declare -F _init_completion >/dev/null 2>&1; then
  complete -F _gl2f gl2f
else
  complete -o nospace -F _gl2f gl2f
fi
