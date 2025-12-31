import argparse
import sys

from .config import load_config
from .download import YouTubeDownloader
from .process import VideosProcessor
from .web_app import WebApp


def download_and_pass(url: str, name: str, output_dir: str = "videos"):
    """Download a YouTube video and move it to the processed folder."""
    filename = f"{name}.mp4"
    downloader = YouTubeDownloader()
    downloader.download(url, output_dir=output_dir, filename=filename)
    processor = VideosProcessor(videos_dir=output_dir)
    processor.simple_pass(filename)


def launch_webapp():
    """Launch the web application with settings from config.yaml."""
    config = load_config()
    paths = config.get("paths", {})
    webapp_config = config.get("webapp", {})
    server_config = webapp_config.get("server", {})

    app = WebApp(
        title=webapp_config.get("title", "MyTube"),
        information=webapp_config.get("information") or None,
        processed_videos_folder=paths.get(
            "processed_videos_folder", "videos/processed"
        ),
        n_max_videos=webapp_config.get("n_max_videos", 4),
        only_one_more_path=paths.get("only_one_more_video", "videos/info/one_more.mp4"),
        finished_path=paths.get("finished_video", "videos/info/finished.mp4"),
        color_done=webapp_config.get("color_done", "#fca903"),
        color_undone=webapp_config.get("color_undone", "#03fcdf"),
    )
    app.launch(
        server_name=server_config.get("host", "0.0.0.0"),
        server_port=server_config.get("port", 7860),
        inbrowser=server_config.get("open_browser", True),
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MyTube command line interface")
    parser.add_argument(
        "-wa",
        "--webapp",
        dest="webapp",
        action="store_true",
        help="Launch the web application using config.yaml settings",
    )
    parser.add_argument(
        "-dp",
        "--download-pass",
        dest="download_pass",
        action="store_true",
        help="Download a video and place it in the processed folder",
    )
    parser.add_argument(
        "-u",
        "--url",
        help="YouTube video URL",
    )
    parser.add_argument(
        "-n",
        "--name",
        help="Base name for the saved video (without extension)",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default="videos",
        help="Directory to store downloaded videos",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.webapp:
        launch_webapp()
        return 0

    if args.download_pass:
        if not args.url or not args.name:
            parser.error(
                "the -dp/--download-pass option requires -u/--url and -n/--name"
            )
        download_and_pass(args.url, args.name, output_dir=args.output_dir)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
