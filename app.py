from flask import Flask, request, send_file
import yt_dlp
import os
import uuid

app = Flask(__name__)

@app.route('/')
def home():
    return 'YouTube to MP3 Server is running (with error handling).'

@app.route('/download')
def download_audio():
    video_url = request.args.get('url')
    if not video_url:
        return 'Missing YouTube URL', 400

    uid = str(uuid.uuid4())
    filename = f'{uid}.mp3'

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
        error_message = str(e)
        if "Sign in to confirm" in error_message or "This video is age restricted" in error_message:
            return "⚠️ 로그인 또는 나이 인증이 필요한 영상은 추출할 수 없습니다.", 403
        return f'❌ 처리 중 오류 발생: {error_message}', 500
    finally:
        if os.path.exists(filename):
            os.remove(filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)