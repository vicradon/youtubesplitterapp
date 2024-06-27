from flask import Flask, render_template, request, redirect, url_for
import subprocess
import os
import uuid
import threading
import json
import dotenv
import requests
import shutil

dotenv.load_dotenv()

app = Flask(__name__)
app.config['THREADS_PER_PAGE'] = 2

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        segments = request.form['segments']

        thread = threading.Thread(target=download_youtube_video, args=(url,segments))
        thread.start()

        return render_template('success_response.html', url=url, segments=segments)
    return render_template('index.html')

def download_youtube_video(url, segments):
    try:
        save_directory = f"./output/{str(uuid.uuid4())}"
        os.makedirs(save_directory)

        info_filename, video_path = download_video(url, save_directory)
        if not info_filename:
            return

        duration = get_video_duration_from_metadata(info_filename)
        segment_duration = duration // int(segments)

        split_video(video_path, segment_duration)
    except Exception as e:
        print(f"Error occurred: {e}")

def split_video(videopath, segment_duration):
    file_dir_segments = videopath.split("/")
    dir_containing_video = '/'.join(file_dir_segments[0:-1])

    output_dir = dir_containing_video + "/parts"

    os.makedirs(output_dir)
    subprocess.run(["ffmpeg", "-i", videopath, "-f", "segment", "-segment_time", str(segment_duration), "-c", "copy", f"{output_dir}/part%03d.mp4"])
    videopaths = os.listdir(output_dir)

    video_title = file_dir_segments[-1].split(".mp4")[0]
    send_videos_to_telegram(videopaths, output_dir, video_title)
    
    cleanup_directory(dir_containing_video)

def cleanup_directory(dir_containing_video):
    try:
        shutil.rmtree(dir_containing_video)
        print(f"Directory {dir_containing_video} has been removed successfully.")
    except Exception as e:
        print(f"Error: {e}")

def download_video(url, save_directory):
    subprocess.run(
        ["yt_dlp", "-o", "%(title)s.%(ext)s", "-P", save_directory, "-S", "res:mp4:m4a", "--recode", "mp4", "--no-simulate", "--write-info-json", url], 
        capture_output=True, text=True
    )
    video_path = f"{save_directory}/{os.listdir(save_directory)[0]}"
    info_file = f"{save_directory}/{os.listdir(save_directory)[1]}"
    return info_file, video_path

    
def get_video_duration_from_metadata(info_file):
    with open(info_file, 'r') as f:
        metadata = json.load(f)
    duration = metadata.get("duration", 0)
    return duration

def send_videos_to_telegram(video_paths, parent_dir, video_title):
    url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendVideo"

    for video_path in video_paths:
        with open(f"{parent_dir}/{video_path}", 'rb') as video_file:
            response = requests.post(url, data={
                'chat_id': os.getenv("VIDEO_CHANNEL_ID"),
                'caption': f"{video_title}-{video_path}"
            }, files={
                'video': video_file
            })
            if response.status_code == 200:
                print(f"Successfully sent video: {video_path}")
            else:
                print(f"Failed to send video: {video_path}. Error: {response.text}")


if __name__ == "__main__":
    if os.getenv('FLASK_ENV') == 'development':
        app.run(debug=True)
    else:
        subprocess.run(["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"])