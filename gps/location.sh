#!/bin/bash

# Start a new tmux session named "gps" with detached mode
tmux new-session -d -s gps -n location_py

# Run location.py in the first tab and restart if it crashes
tmux send-keys -t gps 'while true; do python3 /home/jetson/bme/gps/location.py; sleep 5; done' C-m

# Create a new window (tab) in the same session for mqtt_server.py
tmux new-window -t gps -n mqtt_server_py

# Run mqtt_server.py in the second tab and restart if it crashes
tmux send-keys -t gps:1 'while true; do python3 /home/jetson/bme/gps/mqtt_server.py; sleep 5; done' C-m

# Attach to the tmux session so the user can see the tabs
tmux attach-session -t gps
