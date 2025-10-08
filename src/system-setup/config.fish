#! /usr/bin/fish

if status is-interactive
    # Commands to run in interactive sessions can go here
end


################################################### GREETING ###########################################################

function fish_greeting
    echo ""
    echo "🐟🐟🐟"
    echo "Welcome to the fishy side of $hostname, $(whoami). Have a good swim!"
end


################################################# MY ALIASES ###########################################################

# - Poweruser utils
alias cl='clear'
alias ll='ls -lah'
alias nxtd='pushd +1 > /dev/null'
alias whatsmyip='curl https://ipinfo.io/ip'

# - Program shortcuts
alias py='python'

function pycalc
    python3 -c "print($argv[1])"
end

alias richer='rich --pager'


################################################## MORE CONFIG #########################################################

# - Set nano as default editor
set -gx EDITOR nano

# - Initialize Starship prompt
starship init fish | source
