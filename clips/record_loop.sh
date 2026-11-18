#!/usr/bin/env bash
# Record a live Twitch channel in fixed-length chunks until it goes offline (or MAX_CHUNKS is reached).
#   bash clips/record_loop.sh <channel> <out_dir> [chunk_minutes=15] [max_chunks=16]
# Chunks: <out_dir>/<channel>_<UTC time>.ts – a finished chunk gets a .done marker so the clipper can pick it up.
set -u
CH=$1; OUT=$2; MIN=${3:-15}; MAX=${4:-16}
mkdir -p "$OUT"
for i in $(seq 1 "$MAX"); do
  f="$OUT/${CH}_$(date -u +%Y%m%d_%H%M).ts"
  streamlink --stream-segmented-duration "00:${MIN}:00" -f -o "$f" "twitch.tv/$CH" 720p60,720p,best >> "$OUT/${CH}.log" 2>&1
  rc=$?
  if [ -s "$f" ]; then touch "$f.done"; fi
  if [ $rc -ne 0 ]; then echo "$(date -u +%T) $CH offline or error ($rc), stopping" >> "$OUT/${CH}.log"; break; fi
done
