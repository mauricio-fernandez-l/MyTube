# %%

from pytubefix import YouTube
from pytubefix.cli import on_progress

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

    def __init__(self, url: str, print_info: bool = False):
        self.url = url
        self.print_info = print_info

    def download(self):
        """Download video with one of the clients from the CLIENTS list."""
        for i, client in enumerate(self.CLIENTS):
            try:
                # Try to reach filetype and create YouTube object
                if self.print_info:
                    print(f"Client {client}: {i+1} of {len(self.CLIENTS)}")
                    print(f"Client {client}: Trying")
                yt = YouTube(
                    url=self.url, client=client, on_progress_callback=on_progress
                )
                ys = yt.streams.get_highest_resolution()
                # Download filetype (video or audio)
                if self.print_info:
                    print(f"Client {client}: Downloading {yt.title}")
                ys.download()
                # Return from function if success
                return
            except Exception as e:
                if self.print_info:
                    print(
                        f"Client {client}: Error occurred: {e}\n",
                    )
                else:
                    continue
        raise Exception("Failed to download asset with all available clients")


if __name__ == "__main__":
    url = input("url > ")
    downloader = YouTubeDownloader(url, True)
    downloader.download()
