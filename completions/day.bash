# Bash completion for dwriter
# Source this file: source completions/day.bash

_dwriter_completions() {
    local cur prev opts commands
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    commands="add today standup review edit undo delete stats config examples --help --version"

    case "${prev}" in
        add)
            COMPREPLY=()
            return 0
            ;;
        standup|--format|-f)
            COMPREPLY=$(compgen -W "bullets slack jira markdown" -- "${cur}")
            return 0
            ;;
        review|--format|-f)
            COMPREPLY=$(compgen -W "markdown plain slack" -- "${cur}")
            return 0
            ;;
        review|--days|-d)
            COMPREPLY=()
            return 0
            ;;
        edit|--id|-i)
            COMPREPLY=()
            return 0
            ;;
        delete|--before)
            COMPREPLY=()
            return 0
            ;;
        config)
            COMPREPLY=$(compgen -W "show edit reset path" -- "${cur}")
            return 0
            ;;
        *)
            ;;
    esac

    if [[ ${COMP_CWORD} -eq 1 ]]; then
        COMPREPLY=$(compgen -W "${commands}" -- "${cur}")
        return 0
    fi

    COMPREPLY=$(compgen -W "-t -p --tag --project -f --format -d --days --no-copy -i --id --before --help" -- "${cur}")
}

complete -F _dwriter_completions dwriter
