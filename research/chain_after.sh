#!/usr/bin/env bash
# chain_after.sh <log of running queue> <next queue file> <next log>: wait until the running queue finishes, then run the next.
set -u
until grep -q "queue finished" "$1" 2>/dev/null; do sleep 30; done
bash research/finetune_queue.sh "$2" > "$3" 2>&1
