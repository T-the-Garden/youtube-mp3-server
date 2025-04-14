from flask import Flask, request, send_file
import yt_dlp
import os
import uuid
import random

app = Flask(__name__)

# 샘플 무료 프록시 리스트
PROXIES = [
    "http://51.159.115.233:3128",
    "http://185.199.229.156:7492",
    "http://51.91.157.66:3128",
]

@app.route('/')
def home():
    return 'Universal YouTube Downloader is running.'

@app.route('/download')
def download():
    url = request.args.get('url')
    media_type = request.args.get('type')  # 'audio' or 'video'
    quality = request.args.get('quality')  # e.g., 'mp3', 'wav', 'fhd', 'fhd60', '4k', '4k60'

    if not url or not media_type or not quality:
        return 'Missing parameters', 400

    filename = f"{uuid.uuid4()}"
    proxy = random.choice(PROXIES)

    # yt-dlp 옵션 설정
    ydl_opts = {
        'quiet': True,
        'proxy': proxy,
    }

    if media_type == 'audio':
        ext = 'mp3' if quality == 'mp3' else 'wav'
        filename += f".{ext}"
        ydl_opts.update({
            'format': 'bestaudio/best',
            'outtmpl': filename,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': ext,
                'preferredquality': '320',
            }]
        })
    elif media_type == 'video':
        filename += ".mp4"
        if quality == 'fhd':
            ydl_opts['format'] = 'bestvideo[height<=1080][fps<=30]+bestaudio/best'
        elif quality == 'fhd60':
            ydl_opts['format'] = 'bestvideo[height<=1080][fps>30]+bestaudio/best'
        elif quality == '4k':
            ydl_opts['format'] = 'bestvideo[height<=2160][fps<=30]+bestaudio/best'
        elif quality == '4k60':
            ydl_opts['format'] = 'bestvideo[height<=2160][fps>30]+bestaudio/best'
        ydl_opts['outtmpl'] = filename
        ydl_opts['merge_output_format'] = 'mp4'
    else:
        return 'Invalid type', 400

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return f'❌ 오류: {str(e)}', 500
    finally:
        if os.path.exists(filename):
            os.remove(filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)