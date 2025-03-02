# %%

import os
from pytubefix import YouTube
from pytubefix.cli import on_progress
import pandas as pd

import logging

# %%


class YouTubeDownloader:
    CLIENTS = [
        "WEB",
        "WEB_EMBED",
        "WEB_MUSIC",
        "WEB_CREATOR",
        "WEB_SAFARI",
        "ANDROID",
        "ANDROID_MUSIC",
        "ANDROID_CREATOR",
        "ANDROID_VR",
        "ANDROID_PRODUCER",
        "ANDROID_TESTSUITE",
        "IOS",
        "IOS_MUSIC",
        "IOS_CREATOR",
        "MWEB",
        "TV_EMBED",
        "MEDIA_CONNECT",
    ]

    def __init__(self, log: bool = False):
        self.log = log
        self.logger = logging.getLogger(name="ytd")
        self.logger.setLevel(level=logging.INFO)
        self.logger.addHandler(logging.StreamHandler())
        formatter = logging.Formatter("%(name)s:%(levelname)s: %(message)s")
        for handler in self.logger.handlers:
            handler.setFormatter(formatter)

    def download(self, url: str, output_dir: str = "videos"):
        """Download video with one of the clients from the CLIENTS list."""
        for i, client in enumerate(self.CLIENTS):
            try:
                # Try to reach filetype and create YouTube object
                if self.log:
                    self.logger.info(f"Client {client}: {i+1} of {len(self.CLIENTS)}")
                    self.logger.info(f"Client {client}: Trying")
                yt = YouTube(url=url, client=client, on_progress_callback=on_progress)
                ys = yt.streams.get_highest_resolution()
                # Download filetype (video or audio)
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)
                ys.download(output_path=output_dir if output_dir else os.getcwd())
                if self.log:
                    self.logger.info(f"Client {client}: Success downloading.")
                df = pd.DataFrame(
                    columns=["Start_min", "Start_sec", "End_min", "End_sec", "Name"]
                )
                df.to_csv(f"{output_dir}/{yt.title}.csv", index=False)
                if self.log:
                    self.logger.info(f"Created .csv file")
                # Return from function if success
                return
            except Exception as e:
                if self.log:
                    self.logger.info(f"Client {client}: Error occurred: {e}\n")
                else:
                    continue
        self.logger.warning(f"Failed to download {yt.title}")
