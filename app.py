from flask import Flask, request, render_template_string, send_file, make_response
import yt_dlp
import os
import glob
import threading
import time

app = Flask(__name__)

# ADITECHYT V5.2 - UPDATED
# Port 9000 + Preview + Qualities + How To Use + Success Popup

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Aditechyt - Video & Reels Downloader</title>

    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap" rel="stylesheet">

    <link rel="stylesheet"
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

    <style>

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }

        body {
            background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            color: #2c3e50;
        }

        /* HEADER */

        .header {
            text-align: center;
            padding: 30px 20px 10px;
            animation: fadeInDown 0.8s;
        }

        .header h1 {
            color: #fff;
            font-size: 40px;
            font-weight: 800;
            text-shadow: 2px 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 5px;
        }

        .header p {
            color: #fff;
            font-size: 16px;
            font-weight: 600;
            opacity: 0.9;
        }

        /* MAIN */

        .container {
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            padding: 20px;
        }

        .card {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            padding: 35px 25px;
            border-radius: 24px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            width: 100%;
            max-width: 550px;
            animation: zoomIn 0.6s;
        }

        /* PLATFORMS */

        .platforms {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-bottom: 25px;
        }

        .platform-btn {
            background: #f1f4f8;
            border: none;
            border-radius: 12px;
            width: 50px;
            height: 50px;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 24px;
            cursor: pointer;
            transition: 0.3s;
            color: #7f8c8d;
        }

        .platform-btn:hover,
        .platform-btn.active {
            transform: translateY(-5px);
            box-shadow: 0 10px 15px rgba(0,0,0,0.05);
        }

        .btn-yt.active {
            color: #ff0000;
            background: #ffebeb;
        }

        .btn-ig.active {
            color: #E1306C;
            background: #fce4ec;
        }

        .btn-fb.active {
            color: #1877F2;
            background: #e7f0fd;
        }

        .btn-tw.active {
            color: #000000;
            background: #e8e8e8;
        }

        /* INPUT */

        .input-group {
            position: relative;
            margin-bottom: 25px;
        }

        input[type="text"] {
            width: 100%;
            padding: 20px;
            border: 2px solid #e1e5eb;
            border-radius: 16px;
            font-size: 16px;
            transition: 0.3s;
            background: #fff;
            box-shadow: 0 4px 10px rgba(0,0,0,0.02);
        }

        input[type="text"]:focus {
            border-color: #6c5ce7;
            outline: none;
            box-shadow: 0 0 0 4px rgba(108,92,231,0.1);
        }

        /* QUALITY */

        .quality-title {
            font-size: 15px;
            font-weight: 600;
            color: #34495e;
            margin-bottom: 15px;
            display: block;
            text-align: left;
        }

        .quality-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 30px;
        }

        .quality-grid label {
            cursor: pointer;
        }

        .quality-grid input[type="radio"] {
            display: none;
        }

        .quality-grid span {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 14px 10px;
            background: #f8f9fa;
            border: 2px solid transparent;
            border-radius: 12px;
            font-size: 14.5px;
            font-weight: 600;
            color: #7f8c8d;
            transition: 0.3s;
        }

        .quality-grid input[type="radio"]:checked + span {
            background: #f0edff;
            border-color: #6c5ce7;
            color: #6c5ce7;
        }

        .quality-grid span:hover {
            background: #eef2f5;
        }

        /* DOWNLOAD BUTTON */

        button.btn-dl {
            width: 100%;
            padding: 20px;
            background: linear-gradient(135deg,#6c5ce7,#a29bfe);
            color: white;
            border: none;
            border-radius: 16px;
            font-size: 18px;
            font-weight: 800;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 10px 20px rgba(108,92,231,0.3);
            letter-spacing: 0.5px;
        }

        button.btn-dl:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 25px rgba(108,92,231,0.4);
        }

        /* SPINNER */

        .spinner {
            width: 45px;
            height: 45px;
            border: 5px solid #f3f3f3;
            border-top: 5px solid #6c5ce7;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }

        /* ERROR MESSAGE */

        .msg {
            margin-top: 20px;
            padding: 15px;
            border-radius: 12px;
            font-weight: 600;
            text-align: center;
            font-size: 14px;
        }

        .msg.error {
            background: #fee2e2;
            color: #e74c3c;
            border: 1px solid #f87171;
        }

        /* HOW TO USE */

        .how-to-use {
            margin-top: 25px;
            padding: 20px;
            background: #f8f9ff;
            border: 1px solid #e8e5ff;
            border-radius: 16px;
            text-align: left;
        }

        .how-to-use h3 {
            text-align: center;
            color: #2c3e50;
            font-size: 18px;
            font-weight: 800;
            margin-bottom: 18px;
        }

        .step {
            display: flex;
            align-items: flex-start;
            gap: 12px;
            margin: 14px 0;
            color: #555;
            font-size: 14px;
            line-height: 1.5;
        }

        .step-number {
            min-width: 30px;
            height: 30px;
            border-radius: 50%;
            background: #6c5ce7;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 13px;
        }

        /* SUCCESS POPUP */

        .success-modal {
            display: none;
            position: fixed;
            z-index: 9999;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.55);
            backdrop-filter: blur(5px);
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .success-box {
            background: white;
            width: 100%;
            max-width: 380px;
            padding: 30px 25px;
            border-radius: 22px;
            text-align: center;
            animation: zoomIn 0.3s;
            box-shadow: 0 20px 50px rgba(0,0,0,0.2);
        }

        .success-icon {
            width: 70px;
            height: 70px;
            margin: 0 auto 16px;
            border-radius: 50%;
            background: #e8fff0;
            color: #27ae60;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 34px;
        }

        .success-box h2 {
            color: #2c3e50;
            font-size: 22px;
            margin-bottom: 10px;
            font-weight: 800;
        }

        .success-box p {
            color: #666;
            font-size: 14px;
            line-height: 1.6;
            margin-bottom: 20px;
        }

        .success-box .close-btn {
            background: #2c3e50;
            color: white;
            padding: 13px 30px;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            font-weight: 800;
            font-size: 15px;
            width: 100%;
        }

        /* FOOTER */

        footer {
            background: rgba(0,0,0,0.2);
            backdrop-filter: blur(5px);
            color: white;
            text-align: center;
            padding: 20px;
            margin-top: auto;
        }

        footer p {
            font-size: 14px;
            margin-bottom: 5px;
            font-weight: 600;
        }

        .footer-links a {
            color: #fff;
            text-decoration: underline;
            font-weight: 600;
            font-size: 13px;
            cursor: pointer;
            margin: 0 10px;
            opacity: 0.9;
        }

        /* PRIVACY MODAL */

        .modal {
            display: none;
            position: fixed;
            z-index: 100;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
            backdrop-filter: blur(5px);
            align-items: center;
            justify-content: center;
        }

        .modal-content {
            background: white;
            padding: 30px;
            border-radius: 20px;
            max-width: 400px;
            width: 90%;
            text-align: center;
            animation: zoomIn 0.3s;
        }

        .modal-content h2 {
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 24px;
            font-weight: 800;
        }

        .modal-content p {
            color: #555;
            font-size: 14.5px;
            line-height: 1.6;
            margin-bottom: 25px;
            text-align: left;
        }

        .close-btn {
            background: #2c3e50;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            font-weight: 800;
            font-size: 15px;
            width: 100%;
        }

        /* ANIMATIONS */

        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }

            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes zoomIn {
            from {
                opacity: 0;
                transform: scale(0.95);
            }

            to {
                opacity: 1;
                transform: scale(1);
            }
        }

        @keyframes spin {
            0% {
                transform: rotate(0deg);
            }

            100% {
                transform: rotate(360deg);
            }
        }

        /* MOBILE */

        @media (max-width: 480px) {

            .quality-grid {
                grid-template-columns: 1fr;
                gap: 10px;
            }

            .header h1 {
                font-size: 34px;
            }

            .header p {
                font-size: 14px;
            }

            .card {
                padding: 25px 18px;
            }

            .platforms {
                gap: 10px;
            }

            .platform-btn {
                width: 47px;
                height: 47px;
            }
        }

    </style>

    <script>

        /* SHOW LOADING */

        function showLoading(actionType) {

            if (actionType === 'fetch') {

                document.getElementById('fetch-btn').style.display = 'none';

                document.getElementById('loading-fetch').style.display = 'block';

            }

            else if (actionType === 'download') {

                document.getElementById('dl-btn').style.display = 'none';

                document.getElementById('loading-dl').style.display = 'block';

                document.cookie =
                    "dl_complete=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";

                let checkDownload = setInterval(function() {

                    if (document.cookie.indexOf('dl_complete=true') !== -1) {

                        document.getElementById('dl-btn').style.display = 'block';

                        document.getElementById('loading-dl').style.display = 'none';

                        clearInterval(checkDownload);

                        document.cookie =
                            "dl_complete=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";

                        showSuccessPopup();
                    }

                }, 700);
            }
        }


        /* SUCCESS POPUP */

        function showSuccessPopup() {

            document.getElementById('successModal').style.display = 'flex';

        }


        function closeSuccessPopup() {

            document.getElementById('successModal').style.display = 'none';

        }


        /* PRIVACY MODAL */

        function openModal() {

            document.getElementById('privacyModal').style.display = 'flex';

        }


        function closeModal() {

            document.getElementById('privacyModal').style.display = 'none';

        }


        /* PLATFORM SELECT */

        function selectPlatform(platform, placeholderText) {

            let input = document.getElementById('url-input');

            if (input) {

                input.placeholder = placeholderText;

            }

            let btns =
                document.getElementsByClassName('platform-btn');

            for (let i = 0; i < btns.length; i++) {

                btns[i].classList.remove('active');

            }

            document
                .getElementById('btn-' + platform)
                .classList.add('active');
        }


        /* CLOSE POPUP WHEN CLICKING OUTSIDE */

        window.onclick = function(event) {

            let successModal =
                document.getElementById('successModal');

            let privacyModal =
                document.getElementById('privacyModal');

            if (event.target === successModal) {

                closeSuccessPopup();

            }

            if (event.target === privacyModal) {

                closeModal();

            }

        }

    </script>

</head>

<body>

    <!-- HEADER -->

    <div class="header">

        <h1>ADITECHYT</h1>

        <p>Premium Video & Reels Downloader</p>

    </div>


    <!-- MAIN -->

    <div class="container">

        <div class="card">

            <!-- PLATFORMS -->

            <div class="platforms">

                <button
                    type="button"
                    id="btn-yt"
                    class="platform-btn btn-yt active"
                    onclick="selectPlatform(
                        'yt',
                        '🔗 Paste YouTube link here...'
                    )">

                    <i class="fab fa-youtube"></i>

                </button>


                <button
                    type="button"
                    id="btn-ig"
                    class="platform-btn btn-ig"
                    onclick="selectPlatform(
                        'ig',
                        '📸 Paste Instagram Reels/Post link...'
                    )">

                    <i class="fab fa-instagram"></i>

                </button>


                <button
                    type="button"
                    id="btn-fb"
                    class="platform-btn btn-fb"
                    onclick="selectPlatform(
                        'fb',
                        '📘 Paste Facebook Video link...'
                    )">

                    <i class="fab fa-facebook-f"></i>

                </button>


                <button
                    type="button"
                    id="btn-tw"
                    class="platform-btn btn-tw"
                    onclick="selectPlatform(
                        'tw',
                        '𝕏 Paste X (Twitter) link...'
                    )">

                    <i class="fa-brands fa-x-twitter"></i>

                </button>

            </div>


            {% if not video_info %}

            <!-- STEP 1 -->

            <form
                action="/preview"
                method="POST"
                onsubmit="showLoading('fetch')">

                <div class="input-group">

                    <input
                        type="text"
                        id="url-input"
                        name="url"
                        placeholder="🔗 Paste YouTube link here..."
                        required>

                </div>


                <button
                    id="fetch-btn"
                    type="submit"
                    class="btn-dl">

                    <i class="fa-solid fa-magnifying-glass"></i>

                    Get Video Details

                </button>


                <div
                    id="loading-fetch"
                    style="display:none; text-align:center; margin-top:20px;">

                    <div class="spinner"></div>

                    <h3
                        style="
                        color:#2c3e50;
                        font-size:18px;
                        font-weight:800;">

                        Fetching Details...

                    </h3>

                </div>

            </form>


            {% else %}

            <!-- STEP 2: PREVIEW -->

            <div
                style="
                text-align:center;
                margin-bottom:25px;
                animation:zoomIn 0.4s;">

                <img
                    src="{{ video_info.thumbnail }}"
                    style="
                    width:100%;
                    max-height:250px;
                    object-fit:cover;
                    border-radius:16px;
                    box-shadow:0 4px 15px rgba(0,0,0,0.1);
                    margin-bottom:15px;">

                <h3
                    style="
                    font-size:16px;
                    color:#2c3e50;
                    font-weight:800;
                    word-wrap:break-word;">

                    {{ video_info.title }}

                </h3>

            </div>


            <!-- DOWNLOAD FORM -->

            <form
                action="/download"
                method="POST"
                onsubmit="showLoading('download')">

                <input
                    type="hidden"
                    name="url"
                    value="{{ video_info.url }}">


                <span class="quality-title">

                    Select Format & Quality:

                </span>


                <div class="quality-grid">

                    <label>

                        <input
                            type="radio"
                            name="format"
                            value="best"
                            checked>

                        <span>

                            <i class="fa-solid fa-star"></i>

                            Best Quality

                        </span>

                    </label>


                    <label>

                        <input
                            type="radio"
                            name="format"
                            value="1080p">

                        <span>

                            <i class="fa-solid fa-display"></i>

                            1080p Video

                        </span>

                    </label>


                    <label>

                        <input
                            type="radio"
                            name="format"
                            value="720p">

                        <span>

                            <i class="fa-solid fa-mobile-screen"></i>

                            720p Video

                        </span>

                    </label>


                    <label>

                        <input
                            type="radio"
                            name="format"
                            value="480p">

                        <span>

                            <i class="fa-solid fa-compress"></i>

                            480p Video

                        </span>

                    </label>


                    <label>

                        <input
                            type="radio"
                            name="format"
                            value="360p">

                        <span>

                            <i class="fa-solid fa-mobile-screen-button"></i>

                            360p Video

                        </span>

                    </label>


                    <label>

                        <input
                            type="radio"
                            name="format"
                            value="mp3">

                        <span>

                            <i class="fa-solid fa-music"></i>

                            MP3 Audio

                        </span>

                    </label>

                </div>


                <button
                    id="dl-btn"
                    type="submit"
                    class="btn-dl">

                    <i class="fa-solid fa-download"></i>

                    Download Now

                </button>


                <a
                    href="/"
                    style="
                    display:block;
                    text-align:center;
                    margin-top:15px;
                    color:#6c5ce7;
                    font-weight:600;
                    text-decoration:none;">

                    <i class="fa-solid fa-arrow-left"></i>

                    Paste another link

                </a>


                <!-- DOWNLOAD LOADING -->

                <div
                    id="loading-dl"
                    style="
                    display:none;
                    text-align:center;
                    margin-top:20px;">

                    <div class="spinner"></div>

                    <h3
                        style="
                        color:#2c3e50;
                        font-size:18px;
                        font-weight:800;">

                        Downloading Media...

                    </h3>

                    <p
                        style="
                        font-size:14px;
                        color:#7f8c8d;
                        margin-top:8px;">

                        Please wait while your download is being prepared...

                    </p>

                </div>

            </form>

            {% endif %}


            <!-- ERROR MESSAGE -->

            {% if message %}

            <div class="msg error">

                <i class="fa-solid fa-circle-exclamation"></i>

                {{ message }}

            </div>

            {% endif %}


            <!-- HOW TO USE -->

            <div class="how-to-use">

                <h3>

                    <i class="fa-solid fa-circle-info"></i>

                    How to Use

                </h3>


                <div class="step">

                    <div class="step-number">1</div>

                    <div>

                        <b>Paste Link:</b>

                        Copy your video or reel link and paste it
                        into the link box above.

                    </div>

                </div>


                <div class="step">

                    <div class="step-number">2</div>

                    <div>

                        <b>Get Video Details:</b>

                        Tap the <b>Get Video Details</b> button
                        and wait for the video information to load.

                    </div>

                </div>


                <div class="step">

                    <div class="step-number">3</div>

                    <div>

                        <b>Select Quality:</b>

                        Choose your preferred video quality
                        such as 1080p, 720p, 480p, 360p,
                        or select MP3 Audio.

                    </div>

                </div>


                <div class="step">

                    <div class="step-number">4</div>

                    <div>

                        <b>Download:</b>

                        Tap <b>Download Now</b> and wait for the
                        download to finish. After successful
                        download, check your <b>Gallery</b> or
                        <b>Downloads</b> folder.

                    </div>

                </div>

            </div>

        </div>

    </div>


    <!-- FOOTER -->

    <footer>

        <p>

            &copy; 2026 <b>Aditechyt</b>. All rights reserved.

        </p>

        <div class="footer-links">

            <a onclick="openModal()">

                Privacy Policy

            </a>

            |

            <a onclick="openModal()">

                Terms of Service

            </a>

        </div>

    </footer>


    <!-- PRIVACY MODAL -->

    <div id="privacyModal" class="modal">

        <div class="modal-content">

            <h2>

                Privacy Policy 🛡️

            </h2>

            <p>

                Welcome to <b>Aditechyt</b>.
                We value your privacy immensely.

                <br><br>

                <i
                    class="fa-solid fa-check"
                    style="color:#27ae60;">
                </i>

                We <b>do not</b> track, steal, or store
                your personal data.

                <br><br>

                <i
                    class="fa-solid fa-check"
                    style="color:#27ae60;">
                </i>

                We <b>do not</b> save your downloaded
                videos permanently.

                <br><br>

                <i
                    class="fa-solid fa-check"
                    style="color:#27ae60;">
                </i>

                All processed files are temporarily cached
                and automatically deleted after 5 minutes.

                <br><br>

                Use our service responsibly and only download
                content you are authorized to download.

            </p>


            <button
                class="close-btn"
                onclick="closeModal()">

                I Understand

            </button>

        </div>

    </div>


    <!-- SUCCESS DOWNLOAD POPUP -->

    <div
        id="successModal"
        class="success-modal">

        <div class="success-box">

            <div class="success-icon">

                <i class="fa-solid fa-check"></i>

            </div>


            <h2>

                Download Successful!

            </h2>


            <p>

                Your file has been downloaded successfully.

                <br><br>

                Please check your

                <b>Gallery</b>

                or

                <b>Downloads</b>

                folder.

            </p>


            <button
                class="close-btn"
                onclick="closeSuccessPopup()">

                <i class="fa-solid fa-check"></i>

                OK

            </button>

        </div>

    </div>

</body>
</html>
"""


# --------------------------------------------------
# DELETE FILE AFTER 5 MINUTES
# --------------------------------------------------

def delete_file_later(filepath):

    time.sleep(300)

    try:

        if os.path.exists(filepath):

            os.remove(filepath)

    except Exception:

        pass


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.route('/', methods=['GET'])
def index():

    return render_template_string(HTML_PAGE)


# --------------------------------------------------
# PREVIEW / GET VIDEO DETAILS
# --------------------------------------------------

@app.route('/preview', methods=['POST'])
def preview():

    url = request.form.get('url', '').strip()

    if not url:

        return render_template_string(
            HTML_PAGE,
            message="Please enter a valid link."
        )

    try:

        ydl_opts = {
            'quiet': True,
            'noplaylist': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                url,
                download=False
            )


        video_info = {

            'title': info.get(
                'title',
                'Unknown Title'
            ),

            'thumbnail': info.get(
                'thumbnail',
                ''
            ),

            'url': url

        }


        return render_template_string(
            HTML_PAGE,
            video_info=video_info
        )


    except Exception:

        return render_template_string(

            HTML_PAGE,

            message=(
                "Invalid Link or Private Video. "
                "Please try another link."
            )

        )


# --------------------------------------------------
# DOWNLOAD
# --------------------------------------------------

@app.route('/download', methods=['POST'])
def download():

    url = request.form.get(
        'url',
        ''
    ).strip()

    fmt = request.form.get(
        'format',
        'best'
    )


    if not url:

        return render_template_string(

            HTML_PAGE,

            message="Invalid download link."

        )


    temp_dir = 'temp_downloads'


    if not os.path.exists(temp_dir):

        os.makedirs(temp_dir)


    # Remove old files

    for f in glob.glob(
        f"{temp_dir}/*"
    ):

        try:

            if os.path.isfile(f):

                os.remove(f)

        except Exception:

            pass


    ydl_opts = {

        'outtmpl':
            f'{temp_dir}/%(title)s.%(ext)s',

        'noplaylist': True

    }


    # --------------------------------------------------
    # MP3
    # --------------------------------------------------

    if fmt == 'mp3':

        ydl_opts['format'] = (
            'bestaudio/best'
        )

        ydl_opts['postprocessors'] = [

            {

                'key':
                    'FFmpegExtractAudio',

                'preferredcodec':
                    'mp3',

                'preferredquality':
                    '192'

            }

        ]


    # --------------------------------------------------
    # 1080P
    # --------------------------------------------------

    elif fmt == '1080p':

        ydl_opts['format'] = (
            'bestvideo[height<=1080][ext=mp4]+'
            'bestaudio[ext=m4a]/'
            'best[ext=mp4]/best'
        )


    # --------------------------------------------------
    # 720P
    # --------------------------------------------------

    elif fmt == '720p':

        ydl_opts['format'] = (
            'bestvideo[height<=720][ext=mp4]+'
            'bestaudio[ext=m4a]/'
            'best[ext=mp4]/best'
        )


    # --------------------------------------------------
    # 480P
    # --------------------------------------------------

    elif fmt == '480p':

        ydl_opts['format'] = (
            'bestvideo[height<=480][ext=mp4]+'
            'bestaudio[ext=m4a]/'
            'best[ext=mp4]/best'
        )


    # --------------------------------------------------
    # 360P
    # --------------------------------------------------

    elif fmt == '360p':

        ydl_opts['format'] = (
            'bestvideo[height<=360][ext=mp4]+'
            'bestaudio[ext=m4a]/'
            'best[ext=mp4]/best'
        )


    # --------------------------------------------------
    # BEST QUALITY
    # --------------------------------------------------

    else:

        ydl_opts['format'] = (
            'bestvideo[ext=mp4]+'
            'bestaudio[ext=m4a]/'
            'best[ext=mp4]/best'
        )


    try:

        # Download

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            ydl.download([url])


        # Find downloaded file

        downloaded_files = [

            f for f in glob.glob(
                f"{temp_dir}/*"
            )

            if os.path.isfile(f)

        ]


        if downloaded_files:

            file_path = downloaded_files[0]


            # Delete automatically after 5 minutes

            threading.Thread(

                target=delete_file_later,

                args=(file_path,),

                daemon=True

            ).start()


            # Send file

            response = make_response(

                send_file(

                    file_path,

                    as_attachment=True

                )

            )


            # Tell browser that download is complete

            response.set_cookie(

                'dl_complete',

                'true',

                max_age=60,

                httponly=False,

                samesite='Lax'

            )


            return response


        else:

            return render_template_string(

                HTML_PAGE,

                message=(
                    "File could not be downloaded. "
                    "Please try another format."
                )

            )


    except Exception as e:

        print(
            "DOWNLOAD ERROR:",
            str(e)
        )


        return render_template_string(

            HTML_PAGE,

            message=(
                "Error while downloading. "
                "Please try another format."
            )

        )


# --------------------------------------------------
# START SERVER
# --------------------------------------------------

if __name__ == '__main__':

    app.run(

        host='0.0.0.0',

        port=9700,

        debug=False

    )