#!/usr/bin/env bash
# Exit on error
set -o errexit

# 1. Python packages install karein
pip install -r requirements.txt

# 2. FFmpeg static binary download karein
echo "Downloading FFmpeg..."
mkdir -p bin
curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-amd64-static.tar.xz -o ffmpeg.tar.xz
tar -xf ffmpeg.tar.xz
find ffmpeg-*-static -type f -name "ffmpeg" -exec cp {} bin/ \;
find ffmpeg-*-static -type f -name "ffprobe" -exec cp {} bin/ \;
rm -rf ffmpeg-*-static ffmpeg.tar.xz
chmod +x bin/ffmpeg bin/ffprobe
