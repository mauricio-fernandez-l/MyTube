# MyTube

## Description

Minimal package for downloading, processing (cutting videos and generating thumbnails) and offering a web app for local **offline** video watching, e.g., for your kids or grand mother.

## Quick Start

Run the installer:

```shell
install.bat
```

This creates a virtual environment, installs dependencies, copies `config.example.yaml` to `config.yaml`, and creates a desktop shortcut.

## Configuration

All device-specific settings are in `config.yaml`. Copy from `config.example.yaml` and customize:

```yaml
paths:
  videos_folder: "videos"
  processed_videos_folder: "videos/processed"
  only_one_more_video: "videos/info/one_more.mp4"
  finished_video: "videos/info/finished.mp4"

shortcut:
  name: "MyTube"
  icon_png: "images/my_image.png"

webapp:
  title: "MyTube"
  information: "By You"
  n_max_videos: 4
  server:
    host: "0.0.0.0"
    port: 7860
    open_browser: true
```

See `config.example.yaml` for all available options with documentation.

## CLI Usage

Launch the web app:

```shell
mytube -wa
```

Download a YouTube video and place it directly in processed folder:

```shell
mytube -dp -u "https://youtube.com/..." -n "video_name"
```

## Manual Installation

Create a local python environment:

```shell 
python -m venv .venv
```

Install `mytube` package:

```shell
pip install .
``` 

## Python API

Download a YouTube video:

```python
from mytube.download import YouTubeDownloader

url = "..."
y = YouTubeDownloader()
y.download(url=url)
```

Process videos in `videos` folder according to corresponding `.csv` files (e.g., `0,13,3,12,Dogs` for cutting a video starting at 0:13 and ending at 3:12 with output name "Dogs.mp4", multiple lines for multiple video cuts supported). Thumbnails are generated automatically at default of 10 seconds in the video.

```python
from mytube.process import VideosProcessor

v = VideosProcessor()
v.run()
```

Launch web app programmatically:

```python
from mytube.web_app import WebApp 

w = WebApp(
    title="YourTube",
    information="By You",
    only_one_more_path="videos/info/one_more.mp4",
    finished_path="videos/info/finished.mp4",
)
w.launch()
```

## Create Desktop Shortcut

1. Configure `config.yaml` with your shortcut settings
2. Run the script:

    ```shell
    python create_shortcut.py
    ```

The shortcut will launch `mytube -wa` using settings from `config.yaml`.
