#!/usr/bin/env bash
set -o errexit

# 1. Python dependencies install karein
pip install -r requirements.txt

# 2. Node.js binary install karein (Signature aur n-challenge solve karne ke liye zaroori hai)
mkdir -p bin
curl -L -o node.tar.xz https://nodejs.org/dist/v20.11.0/node-v20.11.0-linux-x64.tar.xz
tar -xf node.tar.xz --strip-components=1 -C .
rm -f node.tar.xz

# 3. Static ffmpeg binary download karein
curl -L -o bin/ffmpeg https://github.com/eugeneware/ffmpeg-static/releases/latest/download/linux-x64
chmod +x bin/ffmpeg

export PATH="$(pwd)/bin:$PATH"
