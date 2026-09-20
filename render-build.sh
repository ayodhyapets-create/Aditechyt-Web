#!/usr/bin/env bash
set -o errexit

# 1. Python packages install karein
pip install -r requirements.txt

# 2. Pre-compiled static ffmpeg binary install karein
mkdir -p bin
curl -L -o bin/ffmpeg https://github.com/eugeneware/ffmpeg-static/releases/latest/download/linux-x64
chmod +x bin/ffmpeg

# PATH export karein taaki yt-dlp ko direct mil jaye
export PATH="$(pwd)/bin:$PATH"
