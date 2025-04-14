from flask import Flask, request, send_file
import yt_dlp
import os
import uuid

app = Flask(__name__)

@app.route('/')
def home():
    return 'YouTube to MP3 Server is running.'

@app.route('/download')
def download_audio():
    video_url = request.args.get('url')
    if not video_url:
        return 'Missing YouTube URL', 400

    # 고유 ID 기반 임시 파일명 생성
    uid = str(uuid.uuid4())
    filename = f'{uid}.mp3'

    # yt_dlp 옵션 설정
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': filename,
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return f'Error: {str(e)}', 500
    finally:
        if os.path.exists(filename):
            os.remove(filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)