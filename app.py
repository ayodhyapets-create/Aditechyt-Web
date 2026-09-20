from flask import Flask, request, render_template_string
import yt_dlp
import os

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aditechyt - Video & Reels Downloader</title>
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
        .platforms { display: flex; justify-content: center; gap: 15px; margin-bottom: 25px; }
        .platform-btn { background: #f1f4f8; border: none; border-radius: 12px; width: 50px; height: 50px; display: flex; justify-content: center; align-items: center; font-size: 24px; cursor: pointer; color: #7f8c8d; }
        .platform-btn.active { color: #ff0000; background: #ffebeb; }
        .input-group { position: relative; margin-bottom: 25px; }
        input[type="text"] { width: 100%; padding: 20px; border: 2px solid #e1e5eb; border-radius: 16px; font-size: 16px; background: #fff; outline: none; }
        input[type="text"]:focus { border-color: #6c5ce7; }
        .quality-title { font-size: 15px; font-weight: 600; color: #34495e; margin-bottom: 15px; display: block; text-align: left; }
        .quality-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 25px; }
        .quality-grid label { cursor: pointer; }
        .quality-grid input[type="radio"] { display: none; }
        .quality-grid span { display: flex; align-items: center; justify-content: center; gap: 8px; padding: 12px 8px; background: #f8f9fa; border: 2px solid transparent; border-radius: 12px; font-size: 14px; font-weight: 600; color: #7f8c8d; }
        .quality-grid input[type="radio"]:checked + span { background: #f0edff; border-color: #6c5ce7; color: #6c5ce7; }
        button.btn-dl { width: 100%; padding: 20px; background: linear-gradient(135deg,#6c5ce7,#a29bfe); color: white; border: none; border-radius: 16px; font-size: 18px; font-weight: 800; cursor: pointer; box-shadow: 0 10px 20px rgba(108,92,231,0.3); }
        .msg { margin-top: 20px; padding: 15px; border-radius: 12px; font-weight: 600; text-align: center; font-size: 14px; background: #fee2e2; color: #e74c3c; border: 1px solid #f87171; word-break: break-all; }
        footer { background: rgba(0,0,0,0.2); color: white; text-align: center; padding: 20px; margin-top: auto; }
    </style>
</head>
<body>
    <div class="header">
        <h1>ADITECHYT</h1>
        <p>Premium Video & Reels Downloader</p>
    </div>
    <div class="container">
        <div class="card">
            <div class="platforms">
                <button type="button" class="platform-btn active"><i class="fab fa-youtube"></i></button>
            </div>

            {% if not video_info %}
            <form action="/preview" method="POST">
                <div class="input-group">
                    <input type="text" name="url" placeholder="🔗 Paste YouTube link here..." required>
                </div>
                <button type="submit" class="btn-dl">
                    <i class="fa-solid fa-magnifying-glass"></i> Get Video Details
                </button>
            </form>
            {% else %}
            <div style="text-align:center; margin-bottom:25px;">
                <img src="{{ video_info.thumbnail }}" style="width:100%; max-height:250px; object-fit:cover; border-radius:16px; margin-bottom:15px;">
                <h3 style="font-size:16px; color:#2c3e50; font-weight:800; word-wrap:break-word;">{{ video_info.title }}</h3>
            </div>

            <form action="/download" method="POST">
                <input type="hidden" name="url" value="{{ video_info.url }}">
                <span class="quality-title">Select Format & Quality:</span>
                <div class="quality-grid">
                    <label><input type="radio" name="format" value="best" checked><span><i class="fa-solid fa-star"></i> Best Quality</span></label>
                    <label><input type="radio" name="format" value="720p"><span><i class="fa-solid fa-display"></i> 720p HD</span></label>
                    <label><input type="radio" name="format" value="480p"><span><i class="fa-solid fa-film"></i> 480p SD</span></label>
                    <label><input type="radio" name="format" value="360p"><span><i class="fa-solid fa-mobile-screen"></i> 360p Low</span></label>
                    <label style="grid-column: span 2;"><input type="radio" name="format" value="mp3"><span><i class="fa-solid fa-music"></i> MP3 / Audio Only</span></label>
                </div>
                <button type="submit" class="btn-dl"><i class="fa-solid fa-download"></i> Generate Download Link</button>
                <a href="/" style="display:block; text-align:center; margin-top:15px; color:#6c5ce7; font-weight:600; text-decoration:none;"><i class="fa-solid fa-arrow-left"></i> Paste another link</a>
            </form>
            {% endif %}

            {% if direct_link %}
            <div style="margin-top:20px; text-align:center; background:#f0edff; padding:20px; border-radius:16px; border:2px dashed #6c5ce7;">
                <p style="font-weight:700; margin-bottom:12px; color:#2c3e50; font-size:16px;">🎉 Stream Ready!</p>
                <a href="{{ direct_link }}" target="_blank" rel="noopener noreferrer" download="video.mp4" class="btn-dl" style="text-decoration:none; display:inline-block; padding:15px 30px; font-size:16px;">Click Here To Download / Play</a>
            </div>
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

# Native bypass configuration (Images aur storyboard ignore karega)
BASE_OPTS = {
    'quiet': True,
    'noplaylist': True,
    'skip_download': True,
    'geo_bypass': True,
    'no_warnings': True,
    'extractor_args': {
        'youtube': {
            'player_client': ['android_testsuite', 'mweb'],
            'player_skip': ['webpage', 'configs']
        }
    },
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36',
    }
}

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_PAGE)

@app.route('/preview', methods=['POST'])
def preview():
    url = request.form.get('url', '').strip()
    if not url:
        return render_template_string(HTML_PAGE, message="Kripya YouTube link enter karein.")
    try:
        with yt_dlp.YoutubeDL(BASE_OPTS) as ydl:
            info = ydl.extract_info(url, download=False, process=False)
            
        if not info:
            return render_template_string(HTML_PAGE, message="Video details nahi mil saki.")

        video_info = {
            'title': info.get('title', 'YouTube Video'),
            'thumbnail': info.get('thumbnail') or f"https://i.ytimg.com/vi/{info.get('id')}/hqdefault.jpg",
            'url': url
        }
        return render_template_string(HTML_PAGE, video_info=video_info)
    except Exception as e:
        return render_template_string(HTML_PAGE, message=f"Preview Error: {str(e)}")

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url', '').strip()
    selected_format = request.form.get('format', 'best')
    try:
        opts = BASE_OPTS.copy()
        opts['format'] = 'all'

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)

        if not info:
            return render_template_string(HTML_PAGE, message="Extraction fail ho gayi.")

        formats = info.get('formats', [])
        stream_url = None

        # Sirf asli media video/audio links uthao (ytimg, storyboard, images ko strictly filter out karo)
        valid_streams = [
            f for f in formats 
            if f.get('url') and 'googlevideo.com' in f.get('url')
        ]

        if selected_format == 'mp3':
            # Audio-only stream filter
            audio_streams = [
                f for f in valid_streams 
                if f.get('vcodec') == 'none' and f.get('acodec') != 'none'
            ]
            if audio_streams:
                stream_url = audio_streams[-1]['url']
        
        elif selected_format in ['720p', '480p', '360p']:
            target_res = int(selected_format.replace('p', ''))
            # Progressive streams jisme audio + video dono ho
            progressive = [
                f for f in valid_streams 
                if f.get('height') and f['height'] <= target_res 
                and f.get('vcodec') != 'none' and f.get('acodec') != 'none'
            ]
            if progressive:
                stream_url = progressive[-1]['url']

        # Agar selected quality na mile toh Best progressive video stream uthao
        if not stream_url:
            all_progressive = [
                f for f in valid_streams 
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none'
            ]
            if all_progressive:
                stream_url = all_progressive[-1]['url']

        # Fallback to any valid googlevideo stream
        if not stream_url and valid_streams:
            stream_url = valid_streams[-1]['url']

        # Aakhri fallback agar googlevideo check me na aaye
        if not stream_url:
            for f in reversed(formats):
                u = f.get('url', '')
                if u and not u.endswith('.jpg') and not u.endswith('.png') and 'ytimg.com' not in u:
                    stream_url = u
                    break

        if not stream_url:
            return render_template_string(HTML_PAGE, message="Playable stream link generate nahi ho saka.")

        video_info = {
            'title': info.get('title', 'YouTube Video'),
            'thumbnail': info.get('thumbnail', ''),
            'url': url
        }
        return render_template_string(HTML_PAGE, video_info=video_info, direct_link=stream_url)
    except Exception as e:
        return render_template_string(HTML_PAGE, message=f"Download Error: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9500, debug=False)
