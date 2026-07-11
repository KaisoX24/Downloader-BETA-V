# Downloader BETA V

A desktop application for downloading YouTube videos, Shorts, and Reels in batch, or converting existing MP4 files to MP3 — built with a resilient, thread-safe download pipeline that keeps working even when individual jobs fail.

![Python](https://img.shields.io/badge/Python-3.x-blue)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-1DFF83)
![yt--dlp](https://img.shields.io/badge/Engine-yt--dlp-red)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## What it does

- **Batch downloads** — paste multiple URLs (one per line) and download them all in a single run
- **Video or audio** — download as MP4 (with resolution selection: 480p/720p/1080p/Best) or extract straight to MP3 (128k–320k bitrate)
- **Standalone MP4 → MP3 conversion** — convert a video file you already have, independent of any download
- **Live per-item progress** — each download gets its own row with thumbnail, progress bar, and status text, updating in real time
- **Batch packaging** — when downloading more than one URL, files are collected into a temporary batch folder and automatically zipped into the destination folder
- **Non-blocking UI** — every download and conversion runs on a background thread, so the interface never freezes mid-download

## Why it's more than "a yt-dlp wrapper"

The interesting engineering in this project isn't the download call itself — `yt-dlp` does that — it's what happens *around* it:

**Per-URL error isolation.** In a batch of 10 URLs, one bad link doesn't take down the other nine. Each URL is processed inside its own try/except at multiple levels (thumbnail fetch, UI row setup, actual download), and a failure at any stage logs the error, records it in a `failed_urls` list, and moves on to the next URL rather than aborting the batch.

**Graceful thumbnail degradation.** If fetching a video's thumbnail fails (network hiccup, restricted video, etc.), the app doesn't stop — it warns the user, falls back to a placeholder title like `Video_3`, and continues the actual download.

**Cross-thread UI safety.** Downloads happen on worker threads, but CustomTkinter widgets can only be touched from the main thread. The app handles this with `window.after(0, ...)` callbacks and a `threading.Event` (with a 5-second timeout) to synchronize UI row creation between the worker thread and the main thread, avoiding both race conditions and indefinite hangs.

**Error categorization for the user.** Instead of a generic "download failed" message, errors are inspected for known patterns — HTTP 429 / rate limiting gets its own explanation with suggested fixes (wait, switch network, use VPN), and YouTube's sign-in/bot-check errors get a separate message explaining cookie export as a solution. Both live in `modules/errors.py`.

**Guaranteed cleanup.** A `finally` block ensures temp thumbnail directories and batch folders are removed even if the download worker crashes partway through — no orphaned temp files left behind after a failure.

## Architecture

```
app.py                  → UI layout (CustomTkinter) + download orchestration/threading
modules/
 ├─ download.py          → yt-dlp wrapper: fetch_thumbnail, download_youtube_video,
 │                          convert_mp4_to_mp3, progress_hook (throttled progress updates)
 ├─ errors.py             → User-facing error dialogs for rate-limit / sign-in failures
 ├─ img_load.py           → Thumbnail loading into CTk labels
 └─ zip_files.py           → Batch output zipping
assets/                   → Icon + UI button/frame images
```

**Progress updates are throttled**, not fired on every yt-dlp callback — `progress_hook` checks elapsed time against a 0.2s minimum interval before pushing a UI update, which keeps the interface responsive during fast downloads instead of flooding the main thread with redraws.

## Tech Stack

| Layer | Tool |
|---|---|
| UI | CustomTkinter |
| Download engine | yt-dlp |
| Media conversion | ffmpeg-python |
| Concurrency | Python `threading` |
| Image handling | Pillow |

## Installation

```bash
git clone https://github.com/KaisoX24/Downloader-BETA-V.git
cd Downloader-BETA-V
pip install -r requirements.txt
python app.py
```

> **Note:** FFmpeg must be installed and available on your system PATH for video/audio conversion to work.

## Usage

1. Choose **Download Video/Reels/Shorts** or **Convert Mp4 to Mp3** from the sidebar dropdown
2. For downloads: paste one or more URLs (one per line), then press `Ctrl+Enter` to confirm the list
3. Pick output format (MP4/MP3) and quality (resolution or bitrate)
4. Choose a save location and hit download — each job appears as its own row with live progress
5. If downloading multiple URLs, the finished files are automatically zipped in your chosen folder

## Known Limitations / Roadmap

- `requirements.txt` currently lists `streamlit` (unused) and is missing `customtkinter` and `Pillow` — needs a cleanup pass
- Windows-specific paths (`LOCALAPPDATA`, `assets\\icon.ico`) mean the app currently targets Windows only
- No persistent download history between sessions
- Potential next step: swap the hardcoded `.place()` layout for a responsive grid, and add a settings panel for default save location

## License

MIT
