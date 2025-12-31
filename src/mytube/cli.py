import argparse
import sys

from .download import YouTubeDownloader
from .process import VideosProcessor


def download_and_pass(url: str, name: str, output_dir: str = "videos"):
    """Download a YouTube video and move it to the processed folder."""
    filename = f"{name}.mp4"
    downloader = YouTubeDownloader()
    downloader.download(url, output_dir=output_dir, filename=filename)
    processor = VideosProcessor(videos_dir=output_dir)
    processor.simple_pass(filename)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MyTube command line interface")
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
