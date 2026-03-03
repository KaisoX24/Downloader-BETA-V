import yt_dlp
import os
import ffmpeg
import time
from pathlib import Path
def fetch_thumbnail(url, temp_path="temp"):
    appdata = Path(os.getenv("LOCALAPPDATA")) / "DownloadBetaV"
    appdata.mkdir(parents=True,exist_ok=True)
    temp_path=appdata/temp_path
    temp_path.mkdir(parents=True, exist_ok=True)
    
    ydl_opts = {
        "skip_download": True,
        "writethumbnail": True,
        "outtmpl": f"{temp_path}/%(id)s.%(ext)s",
        "quiet": True,
        "restrictfilenames": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

    video_id = info["id"]

    for ext in ["webp", "jpg", "png"]:
        thumb_path = os.path.join(temp_path, f"{video_id}.{ext}")
        vid_title=info.get('title','unkown')
        if os.path.exists(thumb_path):
            return [thumb_path,vid_title,temp_path]

    return None    
    
def progress_hook(d, progress_callback=None, status_callback=None, state=None):
    """Handles yt-dlp progress updates safely."""
    now = time.time()

    if state and now - state["last_update"] < 0.2:
        return

    if state:
        state["last_update"] = now

    if d["status"] == "downloading":
        downloaded = d.get("downloaded_bytes", 0)
        total = d.get("total_bytes") or d.get("total_bytes_estimate")

        if total:
            percent = min(downloaded / total, 1.0)
            percent_text = f"{percent * 100:.1f}%"
            if progress_callback:
                progress_callback(percent)
        else:
            percent_text = "Calculating..."

        speed = d.get("speed") or 0
        eta = d.get("eta")

        status_message = (
            f"{percent_text} | "
            f"{downloaded / 1e6:.1f} MB | "
            f"{speed / 1e6:.1f} MB/s | "
            f"ETA: {eta if eta else 'N/A'}"
        )

        if status_callback:
            status_callback(status_message)


def download_youtube_video(
    url,
    selected_res="Best",
    audio_quality="192k",
    file_type="mp4",
    output_path="downloads",
    progress_callback=None,
    status_callback=None,
):
    
    format_map = {
        "Best": "bestvideo+bestaudio/best",
        "480P": "bestvideo[height<=480]+bestaudio/best",
        "720P": "bestvideo[height<=720]+bestaudio/best",
        "1080P": "bestvideo[height<=1080]+bestaudio/best",
    }

    audio_map = {
        "128k": "128",
        "192k": "192",
        "256k": "256",
        "320k": "320",
    }

    ydl_opts = {
        "outtmpl": f"{output_path}/%(title).200s_%(id)s.%(ext)s",
        "restrictfilenames": True,
        "noplaylist": True,
        "verbose":True,
    }

    if file_type == "mp4":
        ydl_opts.update(
            {
                "format": format_map[selected_res],
                "merge_output_format": "mp4",
            }
        )

    elif file_type == "mp3":
        ydl_opts.update(
            {
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": audio_map.get(audio_quality, "192"),
                    }
                ],
            }
        )

    state = {"last_update": 0}

    ydl_opts["progress_hooks"] = [
        lambda d: progress_hook(
            d,
            progress_callback=progress_callback,
            status_callback=status_callback,
            state=state,
        )
    ]

    try:
        if status_callback:
            status_callback("Starting download...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if progress_callback:
            progress_callback(1.0)

        if status_callback:
            status_callback("Download complete!")

        return True

    except Exception as e:
        if status_callback:
            status_callback(f"Error: {str(e)}")
        return False
def convert_mp4_to_mp3(input_file,save_location):
    """
    Convert a video (.mp4) to mp3 audio using ffmpeg-python.
    Returns the output mp3 path.
    Requires FFmpeg installed on the system.
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError("Input file does not exist")

    base, _ = os.path.splitext(input_file)
    output_file = base + ".mp3"
    output_file = os.path.join(save_location, os.path.basename(output_file))
    (
        ffmpeg
        .input(input_file)
        .output(output_file, acodec="mp3",)
        .run(overwrite_output=True)
    )