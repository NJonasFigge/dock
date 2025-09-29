
# TMUX Cheatsheet

A tmux session can have multiple windows, which can have multiple panes.

## Commands:

Many commands are cut short from within a TMUX session by the use of a prefix (by default `Ctrl+B`).

```bash
tmux new -s <name>  # Open new
# From within session, first press the prefix, then:
#   - [D]etach session
tmux ls  # List sessions
tmux attach -t <name>  # Reattach session
# End session from within with "exit"
tmux kill-session -t <name>  # Kill session from outside
```

Manage windows and panes -> see `.conf` file.

Or open help text from within TMUX with `Prefix + ?`.
