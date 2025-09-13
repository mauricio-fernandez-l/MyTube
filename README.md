# MyTube

## Description

Minimal package for downloading, processing (cutting videos and generating thumbnails) and offering a web app for local **offline** video watching, e.g., for your kids or grand mother.

## Installation 

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

1. Create `launch.bat` with content

    ```bat
    @echo off
    echo ============================
    echo 1/3: Activate environment
    echo ============================
    call conda activate your_env_with_mytube_installed

    echo ============================
    echo 2/3: Switch to the directory
    echo ============================
    cd /d C:\this\repo\root

    echo ============================
    echo 3/3: Launch app
    echo ============================
    python launch.py
    ```

2. Create `C:\this\repo\root\launch.py` with content as in the web app example above.
3. Create desktop shortcut to `launch.bat`.

See also files in `demo_files`

* [launch.py](./docs/demo_files/launch.py)
* [launch.bat](./docs/demo_files/launch.bat)
