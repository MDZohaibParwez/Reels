#!/usr/bin/env bash
# Local Just See renders turn BLACK after ~15.3s and fail ("Shader compile failed") with 4+ clips (no GPU here).
# Fix: render the Editer project (<=3 clips, all transitions/labels inside the first 15s), keep its first 15.0s,
# loudfix it, and append the rest of the last shot straight from the v3 source shot.
# stitch.sh <editer.mp4> <cut_sec> <tail_src.mp4> <tail_start> <out.mp4>
set -e
E=$1; C=$2; T=$3; TS=$4; O=$5; D=$(dirname $O)
ffmpeg -v error -y -i $E -t $C -c:v libx264 -preset veryfast -crf 18 -r 30 -pix_fmt yuv420p -c:a aac -ar 44100 -ac 2 -b:a 192k $D/_a.mp4
python3 /home/claude/reels/tools/loudfix.py $D/_a.mp4 $D/_a2.mp4 >/dev/null
ffmpeg -v error -y -ss $TS -i $T -c:v libx264 -preset veryfast -crf 18 -r 30 -pix_fmt yuv420p -c:a aac -ar 44100 -ac 2 -b:a 192k $D/_b.mp4
printf "file '%s'\nfile '%s'\n" $D/_a2.mp4 $D/_b.mp4 > $D/_l.txt
ffmpeg -v error -y -f concat -safe 0 -i $D/_l.txt -c:v libx264 -preset veryfast -crf 20 -maxrate 9000k -bufsize 18000k -c:a aac -b:a 192k -movflags +faststart $O
