#!/usr/bin/env bash
set -o errexit

# 1. Python packages install karein
pip install -r requirements.txt

# 2. Direct zip format mein FFmpeg download karein (No xz tool needed)
echo "Downloading FFmpeg..."
mkdir -p bin
curl -L https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz -o ffmpeg.tar.xz

# Alternatively, lets use a zip or pre-compiled static binary url or we can just skip ffmpeg if yt-dlp basic works, 
# but let's use a reliable direct static link:
