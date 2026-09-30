FROM python:3.10-slim

# Server par ek sath FFmpeg aur Node.js install karna
RUN apt-get update && apt-get install -y \
    ffmpeg \
    nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 9700

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:9700"]
