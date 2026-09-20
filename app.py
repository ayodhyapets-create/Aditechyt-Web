import os
import re
import json
import urllib.request
from flask import Flask, request, render_template_string, Response, stream_with_context
import yt_dlp

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ADITECHYT Downloader</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; }
        body { background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%); min-height: 100vh; display: flex; flex-direction: column; color: #2c3e50; }
        .header { text-align: center; padding: 30px 20px 10px; }
        .header h1 { color: #fff; font-size: 40px; font-weight: 800; text-shadow: 2px 2px 10px rgba(0,0,0,0.1); margin-bottom: 5px; }
        .header p { color: #fff; font-size: 16px; font-weight: 600; opacity: 0.9; }
        .container { flex: 1; display: flex; justify-content: center; align-items: flex-start; padding: 20px; }
        .card { background: rgba(255,255,255,0.95); backdrop-filter: blur(10px); padding: 35px 25px; border-radius: 24px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); width: 100%; max-width: 550px; }
        .input-group { position: relative; margin-bottom: 25px; }
        input[type="text"] { width: 100%; padding: 20px; border: 2px solid #e1e5eb; border-radius: 16px; font-size: 16px; background: #fff; outline: none; }
        input[type="text"]:focus { border-color: #6c5ce7; }
        .quality-title { font-size: 15px; font-weight: 600; color: #34495e; margin-bottom: 15px; display: block; text-align: left; }
        .quality-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 25px; }
        .quality-grid label { cursor: pointer; }
        .quality-grid input[type="radio"] { display: none; }
        .quality-grid span { display: flex; align-items: center; justify-content: center; gap: 8px; padding: 14px 10px; background: #f8f9fa; border: 2px solid transparent; border-radius: 12px; font-size: 14px; font-weight: 600; color: #7f8c8d; }
        .quality-grid input[type="radio"]:checked + span { background: #f0edff; border-color: #6c5ce7; color: #6c5ce7; }
        button.btn-dl { width: 100%; padding: 20px; background: linear-gradient(135deg,#6c5ce7,#a29bfe); color: white; border: none; border-radius: 16px; font-size: 18px; font-weight: 800; cursor: pointer; box-shadow: 0 10px 20px rgba(108,92,231,0.3); }
        .msg { margin-top: 20px; padding: 15px; border-radius: 12px; font-weight: 600; text-align: center; font-size: 14px; background: #fee2e2; color: #e74c3c; border: 1px solid #f87171; word-break: break-all; }
        footer { background: rgba(0,0,0,0.2); color: white; text-align: center; padding: 20px; margin-top: auto; }
    </style>
</head>
<body>
    <div class="header">
        <h1>ADITECHYT</h1>
        <p>Direct Video & Reels Downloader</p>
    </div>
    <div class="container">
        <div class="card">
            {% if not video_info %}
            <form action="/preview" method="POST">
                <div class="input-group">
                    <input type="text" name="url" placeholder="🔗 Paste YouTube link here..." required>
                </div>
                <button type="submit" class="btn-dl"><i class="fa-solid fa-magnifying-glass"></i> Get Video Details</button>
            </form>
            {% else %}
            <div style="text-align:center; margin-bottom:25px;">
                <img src="{{ video_info.thumbnail }}" style="width:100%; max-height:250px; object-fit:cover; border-radius:16px; margin-bottom:15px;">
                <h3 style="font-size:16px; color:#2c3e50; font-weight:800; word-wrap:break-word;">{{ video_info.title }}</h3>
            </div>

            <form action="/stream" method="GET">
                <input type="hidden" name="url" value="{{ video_info.url }}">
                <span class="quality-title">Select Format:</span>
                <div class="quality-grid">
                    <label><input type="radio" name="format" value="video" checked><span><i class="fa-solid fa-video"></i> MP4 Video</span></label>
                    <label><input type="radio" name="format" value="audio"><span><i class="fa-solid fa-music"></i> MP3 Audio</span></label>
                </div>
                <button type="submit" class="btn-dl"><i class="fa-solid fa-download"></i> Start Download</button>
                <a href="/" style="display:block; text-align:center; margin-top:15px; color:#6c5ce7; font-weight:600; text-decoration:none;"><i class="fa-solid fa-arrow-left"></i> Paste another link</a>
            </form>
            {% endif %}

            {% if message %}
            <div class="msg"><i class="fa-solid fa-circle-exclamation"></i> {{ message }}</div>
            {% endif %}
        </div>
    </div>
    <footer><p>&copy; 2026 <b>Aditechyt</b>. All rights reserved.</p></footer>
</body>
</html>
"""

def extract_direct_media(url, mode='video'):
    # Video ID extract karein
    v_match = re.search(r"(?:v=|\/|youtu\.be\/|shorts\/)([a-zA-Z0-9_-]{11})", url)
    v_id = v_match.group(1) if v_match else None
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    # Tarika 1: Direct YouTube Player Raw JSON Data Extraction (Zero Format Resolver)
    if v_id:
        try:
            req = urllib.request.Request(f"https://www.youtube.com/watch?v={v_id}", headers=headers)
            html = urllib.request.urlopen(req, timeout=8).read().decode('utf-8', errors='ignore')
            
            # Title
            title_m = re.search(r'<title>(.*?)</title>', html)
            title = title_m.group(1).replace(' - YouTube', '').strip() if title_m else 'video'
            
            # Streaming data raw JSON search
            json_match = re.search(r'ytInitialPlayerResponse\s*=\s*({.+?});', html)
            if json_match:
                data = json.loads(json_match.group(1))
                streaming_data = data.get('streamingData', {})
                formats = streaming_data.get('formats', []) + streaming_data.get('adaptiveFormats', [])
                
                target_url = None
                if mode == 'audio':
                    for f in formats:
                        if 'audio' in f.get('mimeType', '') and f.get('url'):
                            target_url = f['url']
                            break
                else:
                    for f in formats:
                        if 'video/mp4' in f.get('mimeType', '') and f.get('url'):
                            target_url = f['url']
                            break
                
                if target_url:
                    return target_url, title
        except Exception:
            pass

    # Tarika 2: yt-dlp Native Dump without processing
    ydl_opts = {
        'quiet': True,
        'noplaylist': True,
        'geo_bypass': True,
        'skip_download': True,
        'format': 'best',
        'ignoreerrors': True
    }
    if os.path.exists('cookies.txt'):
        ydl_opts['cookiefile'] = 'cookies.txt'

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if info:
            title = info.get('title', 'video')
            media_url = info.get('url')
            if not media_url and 'formats' in info:
                for f in reversed(info['formats']):
                    if f.get('url') and 'googlevideo.com' in f.get('url'):
                        media_url = f['url']
                        break
            if media_url:
                return media_url, title

    return None, "video"

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_PAGE)

@app.route('/preview', methods=['POST'])
def preview():
    url = request.form.get('url', '').strip()
    if not url:
        return render_template_string(HTML_PAGE, message="Please enter a valid link.")
    
    v_match = re.search(r"(?:v=|\/|youtu\.be\/|shorts\/)([a-zA-Z0-9_-]{11})", url)
    v_id = v_match.group(1) if v_match else None
    
    # Official oembed call taaki bot check na lage
    title = "YouTube Video"
    if v_id:
        try:
            req = urllib.request.Request(f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={v_id}&format=json", headers={'User-Agent': 'Mozilla/5.0'})
            res = json.loads(urllib.request.urlopen(req, timeout=5).read().decode())
            title = res.get('title', title)
        except Exception:
            pass

    video_info = {
        'title': title,
        'thumbnail': f"https://i.ytimg.com/vi/{v_id}/hqdefault.jpg" if v_id else "",
        'url': url
    }
    return render_template_string(HTML_PAGE, video_info=video_info)

@app.route('/stream', methods=['GET'])
def stream():
    url = request.args.get('url', '').strip()
    mode = request.args.get('format', 'video')

    if not url:
        return "Missing URL", 400

    media_url, title = extract_direct_media(url, mode)

    if not media_url:
        return "Streaming URL extract nahi ho saka. YouTube stream encrypted hai.", 500

    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_', '-')).strip() or "download"

    req = urllib.request.Request(media_url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    })

    def generate():
        with urllib.request.urlopen(req) as resp:
            while True:
                chunk = resp.read(1024 * 512)
                if not chunk:
                    break
                yield chunk

    ext = "mp3" if mode == "audio" else "mp4"
    return Response(
        stream_with_context(generate()),
        content_type="video/mp4" if ext == "mp4" else "audio/mpeg",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_title}.{ext}"'
        }
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9500, debug=False)
