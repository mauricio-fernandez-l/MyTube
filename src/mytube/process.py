# %%

from moviepy import VideoFileClip
import os
import csv
import datetime
import cv2
import shutil

from .logger import get_logger

now = datetime.datetime.now

# %%


class ThumbnailGenerator:

    @staticmethod
    def run(video_path: str, thumbnail_name: str = None, time: int = 10):
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file {video_path} not found")
        output_dir = os.path.join(os.path.dirname(video_path), "thumbnails")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        if thumbnail_name is None:
            thumbnail_name = os.path.basename(video_path).replace(".mp4", ".png")
        thumbnail_path = os.path.join(output_dir, thumbnail_name)
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_MSEC, time * 1000)
        success, image = cap.read()
        if success:
            cv2.imwrite(thumbnail_path, image)
        cap.release()
        # Retrieve the thumbnail path for unknown extension based on path
        print(f"Thumbnail generated: {thumbnail_path}")
        return thumbnail_path


# %%


class VideoCutter:
    def __init__(self, video_path: str):
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file {video_path} not found")
        self.video_path = video_path
        self.output_dir = os.path.join(os.path.dirname(video_path), "processed")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.csv_path = video_path.replace(".mp4", ".csv")
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"CSV file {self.csv_path} not found")
        self.intervals = self.read_intervals_from_csv()
        self.logger = get_logger("v_cut")

    def read_intervals_from_csv(self):
        intervals = []
        with open(self.csv_path, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                start = (int(row["Start_min"]), int(row["Start_sec"]))
                end = (int(row["End_min"]), int(row["End_sec"]))
                name = row["Name"]
                intervals.append((start, end, name))
        return intervals

    def process_intervals(self):
        # TODO: works, but needs improvement
        base_name = os.path.splitext(os.path.basename(self.video_path))[0]
        for idx, (start, end, name) in enumerate(self.intervals):
            self.logger.info(f"Processing clip {idx + 1}: {start} - {end} ({name})")
            video = VideoFileClip(self.video_path)
            subclip: VideoFileClip = video.subclipped(start, end)
            output_path = os.path.join(self.output_dir, f"{base_name}_{name}.mp4")
            subclip.write_videofile(output_path)
            subclip.close()
            thumbnail_name = f"{base_name}_{name}.png"
            ThumbnailGenerator.run(output_path, thumbnail_name)
            video.close()

    def run(self):
        t_1 = now()
        self.logger.info(f"Started at {t_1}")
        self.process_intervals()
        t_2 = now()
        self.logger.info(f"Finished at {t_2}")
        self.logger.info(f"Duration: {t_2 - t_1}")
        self.logger.info("Done")


class VideosProcessor:

    def __init__(self, videos_dir: str = "videos"):
        self.videos_dir = videos_dir
        self.logger = get_logger("v_pro")

    def get_video_files(self):
        return [f for f in os.listdir(self.videos_dir) if f.endswith(".mp4")]

    def run(self):
        video_files = self.get_video_files()
        for video_file in video_files:
            video_path = f"{self.videos_dir}/{video_file}"
            self.logger.info(f"Processing {video_path}")
            vc = VideoCutter(video_path)
            vc.run()
        self.logger.info("All videos processed")

    def simple_pass(self, video_name: str):
        path = os.path.join(self.videos_dir, video_name)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Video file {path} not found")
        shutil.copy(path, os.path.join(self.videos_dir, "processed"))
        path_processed = os.path.join(self.videos_dir, "processed", video_name)
        ThumbnailGenerator.run(path_processed)


# %%
