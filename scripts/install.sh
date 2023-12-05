#!/bin/sh

# project root
cd $(dirname $0)/..

tmux new-session -d -s neetbox 'poetry install || sleep 5'
tmux split-window -c frontend 'yarn || sleep 5'
tmux a -t neetbox
