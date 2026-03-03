# Zsh completion for dwriter
# Source this file: source completions/day.zsh

#compdef dwriter

_dwriter() {
    local -a commands
    local -a formats_standup
    local -a formats_review
    local -a config_subcommands

    commands=(
        'add:Add a new log entry'
        'today:Show today entries'
        'standup:Generate yesterday standup'
        'review:Review last N days'
        'edit:Edit or delete entries'
        'undo:Delete the most recent entry'
        'delete:Bulk delete old entries'
        'stats:Show logging statistics'
        'config:View and edit configuration'
        'examples:Show usage examples'
    )

    formats_standup=(
        'bullets:Bullet point format'
        'slack:Slack format'
        'jira:Jira format'
        'markdown:Markdown format'
    )

    formats_review=(
        'markdown:Markdown format'
        'plain:Plain text format'
        'slack:Slack format'
    )

    config_subcommands=(
        'show:View current configuration'
        'edit:Edit configuration file'
        'reset:Reset to defaults'
        'path:Show config file path'
    )

    _arguments -C \
        '1: :->command' \
        '*:: :->args'

    case $state in
        command)
            _describe 'commands' commands
            ;;
        args)
            case $words[1] in
                add)
                    _arguments \
                        '-t+[Add a tag]:tag:' \
                        '--tag=[Add a tag]:tag:' \
                        '-p+[Set project name]:project:' \
                        '--project=[Set project name]:project:' \
                        '*:content:'
                    ;;
                standup)
                    _arguments \
                        '-f+[Output format]:format:((formats_standup))' \
                        '--format=[Output format]:format:((formats_standup))' \
                        '--no-copy[Don'\''t copy to clipboard]'
                    ;;
                review)
                    _arguments \
                        '-d+[Number of days to review]:days:' \
                        '--days=[Number of days to review]:days:' \
                        '-f+[Output format]:format:((formats_review))' \
                        '--format=[Output format]:format:((formats_review))'
                    ;;
                edit)
                    _arguments \
                        '-i+[Edit specific entry by ID]:entry ID:' \
                        '--id=[Edit specific entry by ID]:entry ID:'
                    ;;
                delete)
                    _arguments \
                        '--before=[Delete entries before date (YYYY-MM-DD)]:date:'
                    ;;
                config)
                    _arguments \
                        '1: :->config_cmd'
                    case $state in
                        config_cmd)
                            _describe 'config commands' config_subcommands
                            ;;
                    esac
                    ;;
                stats|today|examples|undo)
                    ;;
            esac
            ;;
    esac
}

_dwriter "$@"
