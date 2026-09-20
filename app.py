import os
import json
import re
import urllib.request
import requests
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
        .header h1 { color: #fff; font-size: 38px; font-weight: 800; text-shadow: 2px 2px 10px rgba(0,0,0,0.1); margin-bottom: 5px; }
        .header p { color: #fff; font-size: 15px; font-weight: 600; opacity: 0.9; }
        .container { flex: 1; display: flex; justify-content: center; align-items: flex-start; padding: 20px; }
        .card { background: rgba(255,255,255,0.95); backdrop-filter: blur(10px); padding: 35px 25px; border-radius: 24px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); width: 100%; max-width: 520px; }
        .input-group { position: relative; margin-bottom: 20px; }
        input[type="text"] { width: 100%; padding: 18px; border: 2px solid #e1e5eb; border-radius: 16px; font-size: 15px; background: #fff; outline: none; }
        input[type="text"]:focus { border-color: #6c5ce7; }
        .quality-title { font-size: 14px; font-weight: 700; color: #34495e; margin-bottom: 12px; display: block; text-align: left; }
        .quality-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 25px; }
        .quality-grid label { cursor: pointer; }
        .quality-grid input[type="radio"] { display: none; }
        .quality-grid span { display: flex; align-items: center; justify-content: center; gap: 8px; padding: 12px 10px; background: #f8f9fa; border: 2px solid transparent; border-radius: 12px; font-size: 13.5px; font-weight: 600; color: #7f8c8d; }
        .quality-grid input[type="radio"]:checked + span { background: #f0edff; border-color: #6c5ce7; color: #6c5ce7; }
        button.btn-dl { width: 100%; padding: 18px; background: linear-gradient(135deg,#6c5ce7,#a29bfe); color: white; border: none; border-radius: 16px; font-size: 17px; font-weight: 800; cursor: pointer; box-shadow: 0 10px 20px rgba(108,92,231,0.3); }
        .msg { margin-top: 20px; padding: 15px; border-radius: 12px; font-weight: 600; text-align: center; font-size: 14px; background: #fee2e2; color: #e74c3c; border: 1px solid #f87171; word-break: break-all; }
        footer { background: rgba(0,0,0,0.2); color: white; text-align: center; padding: 20px; margin-top: auto; }
    </style>
</head>
<body>
    <div class="header">
        <h1>ADITECHYT</h1>
        <p>Direct Stream Downloader</p>
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
            <div style="text-align:center; margin-bottom:20px;">
                <img src="{{ video_info.thumbnail }}" style="width:100%; max-height:240px; object-fit:cover; border-radius:16px; margin-bottom:12px;">
                <h3 style="font-size:15px; color:#2c3e50; font-weight:800;">{{ video_info.title }}</h3>
            </div>

            <form action="/stream" method="GET">
                <input type="hidden" name="url" value="{{ video_info.url }}">
                <span class="quality-title">Choose Download Type:</span>
                <div class="quality-grid">
                    <label><input type="radio" name="format" value="video" checked><span><i class="fa-solid fa-video"></i> Full MP4 Video</span></label>
                    <label><input type="radio" name="format" value="audio"><span><i class="fa-solid fa-music"></i> Audio (MP3)</span></label>
                </div>
                <button type="submit" class="btn-dl"><i class="fa-solid fa-download"></i> Download Directly</button>
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

def extract_video_id(url):
    match = re.search(r"(?:v=|/|youtu\.be/|shorts/)([a-zA-Z0-9_-]{11})", url)
    return match.group(1) if match else None

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_PAGE)

@app.route('/preview', methods=['POST'])
def preview():
    url = request.form.get('url', '').strip()
    v_id = extract_video_id(url)
    if not v_id:
        return render_template_string(HTML_PAGE, message="Invalid YouTube URL.")
    
    # Official oEmbed: Isme kabhie bot-detection ya login issue nahi aata
    title = "YouTube Video"
    try:
        req = urllib.request.Request(
            f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={v_id}&format=json",
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        res = json.loads(urllib.request.urlopen(req, timeout=5).read().decode())
        title = res.get('title', title)
    except Exception:
        pass

    video_info = {
        'id': v_id,
        'title': title,
        'thumbnail': f"https://i.ytimg.com/vi/{v_id}/hqdefault.jpg",
        'url': url
    }
    return render_template_string(HTML_PAGE, video_info=video_info)

@app.route('/stream', methods=['GET'])
def stream():
    url = request.args.get('url', '').strip()
    mode = request.args.get('format', 'video')

    if not url:
        return "Missing URL", 400

    try:
        ydl_opts = {
            'quiet': True,
            'noplaylist': True,
            'geo_bypass': True,
            'skip_download': True,
            'no_warnings': True,
            'format': 'all',
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'ios']
                }
            },
            'http_headers': {
                'User-Agent': 'com.google.android.youtube/19.10.37 (Linux; U; Android 11; en_US) gzip',
            }
        }
        if os.path.exists('cookies.txt'):
            ydl_opts['cookiefile'] = 'cookies.txt'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = info.get('formats', [])
        
        # Real media streams filter (storyboards aur static images ko strictly exclude karein)
        valid_streams = []
        for f in formats:
            fid = str(f.get('format_id', ''))
            furl = f.get('url', '')
            ext = f.get('ext', '')
            if fid.startswith('sb') or 'storyboard' in furl.lower() or 'ytimg.com' in furl:
                continue
            if ext in ['mhtml', 'jpg', 'png', 'webp']:
                continue
            if furl and 'googlevideo.com' in furl:
                valid_streams.append(f)

        media_url = None

        if mode == 'audio':
            for f in reversed(valid_streams):
                if f.get('vcodec') == 'none' and f.get('acodec') not in ['none', None]:
                    media_url = f['url']
                    break
        else:
            # Combined progressive video + audio
            for f in reversed(valid_streams):
                if f.get('vcodec') not in ['none', None] and f.get('acodec') not in ['none', None]:
                    media_url = f['url']
                    break

        if not media_url and valid_streams:
            media_url = valid_streams[-1]['url']

        if not media_url:
            media_url = info.get('url')

        if not media_url:
            return "Downloadable media stream nahi mil saki.", 500

        raw_title = info.get('title', 'video')
        title = "".join(c for c in raw_title if c.isalnum() or c in (' ', '_', '-')).strip() or "video"
        ext = "mp3" if mode == "audio" else "mp4"

        # Direct chunk pipe
        stream_req = requests.get(media_url, stream=True, timeout=30)

        def generate():
            for chunk in stream_req.iter_content(chunk_size=1024 * 512):
                if chunk:
                    yield chunk

        return Response(
            stream_with_context(generate()),
            content_type="video/mp4" if ext == "mp4" else "audio/mpeg",
            headers={
                "Content-Disposition": f'attachment; filename="{title}.{ext}"'
            }
        )
    except Exception as e:
        return f"Stream Extraction Error: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 9500))
    app.run(host='0.0.0.0', port=port, debug=False)
