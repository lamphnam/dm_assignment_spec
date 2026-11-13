#!/usr/bin/env bash
# Queue of research/finetune_cv.py runs on the GPU venv.
#   bash research/finetune_queue.sh            # runs the default queue below
#   bash research/finetune_queue.sh <file>     # each line of <file>: <enc> <tag> <extra args...>
# Each run: outputs/logs/finetune_<enc>_<tag>.log, outputs/research/finetune_<enc>_<tag>.json (+ _oof.pkl)
# Queue history (2026-11-14 night): minilm sf1/sf2/ce_e2/ce_e8/ce_noprefix, then mpnet/specter ce (OOM -> fixed, rerun).
set -u
export PYTHONIOENCODING=utf-8
PY=.venv-gpu/Scripts/python.exe
run() {  # run <enc> <tag> <extra args...>
  local enc=$1 tag=$2; shift 2
  echo "$(date '+%H:%M:%S') start $enc $tag $*"
  "$PY" -m research.finetune_cv --enc "$enc" --tag "$tag" "$@" > "outputs/logs/finetune_${enc}_${tag}.log" 2>&1
  local rc=$?
  echo "$(date '+%H:%M:%S') done  $enc $tag exit=$rc"
}
if [ $# -ge 1 ]; then
  while read -r enc tag rest; do
    [ -z "$enc" ] || [ "${enc#\#}" != "$enc" ] && continue
    # shellcheck disable=SC2086
    run "$enc" "$tag" $rest
  done < "$1"
else
  run mpnet   ce --methods ce
  run specter ce --methods ce
fi
echo "$(date '+%H:%M:%S') queue finished"
