#!/usr/bin/env bash
# Exit on error
set -o errexit

# Render ke liye FFmpeg download aur install karne ki command
apt-get update && apt-get install -y ffmpeg
