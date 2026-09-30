FROM python:3.10-slim

# Install system dependencies (FFmpeg and Node.js)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Har baar build par yt-dlp ko latest update karein
RUN pip install --no-cache-dir --upgrade yt-dlp

COPY . .

EXPOSE 10000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]
