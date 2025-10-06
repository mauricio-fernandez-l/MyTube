# MyTube

## Description

Minimal package for downloading, processing (cutting videos and generating thumbnails) and offering a web app for local **offline** video watching, e.g., for your kids or grand mother.

## Installation 

Create a local python environment

```shell 
python -m venv .venv
```

and install `mytube` package in it

```shell
pip install .
``` 

## Usage

Download a YouTube video.

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

Launch web app.

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

## Create desktop shortcut

1. Create `C:\this\repo\root\launch.py` with content as in the web app example above.
2. Run the script `create_shortcut.py`

    ```shell
    python create_shortcut.py
    ```

    with adapted configuration

    ```python
    # Configuration
    PNG_PATH = "images/my_image.png"  # Change this to your PNG file path
    SHORTCUT_NAME = "MyTube"  # Change this to your desired shortcut name
    ```

See also files in `demo_files`

* [launch.py](./docs/demo_files/launch.py)
