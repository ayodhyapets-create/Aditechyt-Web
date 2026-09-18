#!/usr/bin/env bash
set -o errexit

# Create bin directory
mkdir -p bin

# Download FFmpeg static build
curl -O https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
tar -xf ffmpeg-release-amd64-static.tar.xz
find ffmpeg-*-static -type f -name "ffmpeg" -exec cp {} bin/ \;
find ffmpeg-*-static -type f -name "ffprobe" -exec cp {} bin/ \;
rm -rf ffmpeg-*-static *.tar.xz

# Make it accessible in PATH
export PATH="$PWD/bin:$PATH"
