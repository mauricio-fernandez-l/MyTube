# %%

from moviepy import VideoFileClip
import os
import csv
import datetime

now = datetime.datetime.now

# %%

video_path = "TODO"
output_dir = "videos/"

# %%

csv_path = video_path.replace(".mp4", ".csv")
if not os.path.exists(csv_path):
    raise FileNotFoundError(f"CSV file {csv_path} not found")

# %%


def read_intervals_from_csv(csv_file):
    intervals = []
    with open(csv_file, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            start = (int(row["Start_min"]), int(row["Start_sec"]))
            end = (int(row["End_min"]), int(row["End_sec"]))
            name = row["Name"]
            intervals.append((start, end, name))
    return intervals


def process_intervals(input_path: str, output_dir: str, intervals: list):
    video = VideoFileClip(input_path)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    for idx, (start, end, name) in enumerate(intervals):
        print(f"Processing clip {idx + 1}: {start} - {end} ({name})")
        subclip: VideoFileClip = video.subclipped(start, end)
        output_path = f"{output_dir}{base_name}_{name}.mp4"
        subclip.write_videofile(output_path, logger="bar")
        subclip.close()
    video.close()


if __name__ == "__main__":
    t_1 = now()
    print(f"Started at {t_1}")
    time_intervals = read_intervals_from_csv(csv_path)
    process_intervals(video_path, output_dir, time_intervals)
    t_2 = now()
    print(f"Finished at {t_2}")
    print(f"Duration: {t_2 - t_1}")
    print("Done")

# %%
