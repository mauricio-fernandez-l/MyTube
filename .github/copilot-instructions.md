# MyTube - Copilot Instructions

## Project Overview
MyTube is a Python application for downloading YouTube videos, processing them (cutting clips, generating thumbnails), and serving them via a local Gradio web app for offline viewing. Designed for simple use cases like kid-friendly video libraries.

## Architecture & Data Flow

```
download.py → videos/*.mp4 + videos/*.csv → process.py → videos/processed/*.mp4 + thumbnails/*.png → web_app.py
```

### Core Components
- **`download.py`**: `YouTubeDownloader` - tries multiple `pytubefix` clients sequentially until success; creates companion `.csv` file for cut definitions
- **`process.py`**: `VideoCutter` reads `.csv` files with format `Start_min,Start_sec,End_min,End_sec,Name` to cut videos; `ThumbnailGenerator` captures frames at 10s mark
- **`web_app.py`**: `WebApp` - Gradio UI with thumbnail gallery, video player, parental controls (video limit, undo). State persisted to `webapp_state.json`
- **`cli.py`**: Entry point `mytube` command with `-dp/--download-pass` for download+simple pass workflow

## Key Conventions

### Video Processing CSV Format
Each source video requires a companion `.csv` with columns: `Start_min,Start_sec,End_min,End_sec,Name`
```csv
Start_min,Start_sec,End_min,End_sec,Name
0,13,3,12,Dogs
5,0,8,30,Cats
```
Output: `{original_name}_{Name}.mp4` in `videos/processed/`

### Directory Structure
- `videos/` - Source videos and `.csv` cut definitions
- `videos/processed/` - Output clips ready for web app
- `videos/processed/thumbnails/` - Auto-generated PNG thumbnails
- `videos/info/` - Optional info videos (e.g., `one_more.mp4`, `finished.mp4`)

### WebApp State
State persisted in `webapp_state.json` at project root:
```json
{"counter": 0, "seen_videos": [], "n_max_videos": 4}
```

## Development

### Installation
```shell
python -m venv .venv
pip install .
```

### Running the Web App
Create a `launch.py` (see [launch.py](launch.py) example):
```python
from mytube.web_app import WebApp
w = WebApp(title="MyTube", n_max_videos=4)
w.launch()  # Opens browser at http://0.0.0.0:7860
```

### CLI Usage
```shell
mytube -dp -u "https://youtube.com/..." -n "video_name"
```

## Dependencies
- `pytubefix` - YouTube downloading (multiple client fallback)
- `moviepy` - Video cutting with `VideoFileClip.subclipped()`
- `opencv-python` - Thumbnail generation via `cv2.VideoCapture`
- `gradio` - Web UI with Gallery, Video, Tabs components
- `matplotlib` - Progress pie chart visualization

## Code Patterns
- Classes use `self.logger` from `logger.get_logger()` for consistent `name:level: message` format
- WebApp uses `gr.State` for reactive state and `yield` for multi-step UI updates
- Error handling: Download tries all clients before failing; file operations check `os.path.exists()` first
