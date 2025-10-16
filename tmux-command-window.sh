#!/bin/bash

# Check if tmux is installed and install if not
if ! command -v tmux &> /dev/null; then
    echo "tmux not found, installing..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y tmux
    fi
fi

# Tmux script to create a split pane session with btop and GPU network TUI
# Left pane: btop (system monitor)
# Right pane: gpu-net-tui.py (GPU and network monitor)

# Start a new tmux session named "system-monitor"
tmux new-session -d -s "gpu/network/docker system-monitor" \; \
  send-keys 'btop' Enter \; \
  split-window -h \; \
  send-keys 'python3 ./gpu-textual-tui.py' Enter \; \
  select-pane -t 0 \; \
  attach-session

# Alternative one-liner version (uncomment to use instead):
# tmux new-session -d -s "system-monitor" 'btop' \; split-window -h 'cd /home/petegit/gpu-textual-tui && python3 gui-textual-tui.py' \; attach-session

