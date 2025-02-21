# %%

import gradio as gr
import glob
import cv2
import os
import datetime

now = datetime.datetime.now

# %%

videos_folder = "videos"
n_max_videos = 4

# %%

video_files = glob.glob(f"{videos_folder}/*.mp4")

# %%

thumbnail_folder = f"{videos_folder}/thumbnails"
if not os.path.exists(thumbnail_folder):
    os.makedirs(thumbnail_folder)


def generate_thumbnail(video_path, thumbnail_path, time=10):
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_MSEC, time * 1000)
    success, image = cap.read()
    if success:
        cv2.imwrite(thumbnail_path, image)
    cap.release()


thumbnails = []
for video in video_files:
    thumbnail_path = f"{thumbnail_folder}/{os.path.basename(video)}.png"
    if not os.path.isfile(thumbnail_path):
        generate_thumbnail(video, thumbnail_path)
    thumbnails.append(thumbnail_path)

# %%


def check_video_counter(counter: int, video: str, n_max_videos: int):
    if counter > n_max_videos:
        return gr.update(value=None, interactive=False), n_max_videos
    else:
        return gr.update(value=video), counter


def select_thumbnail(
    event: gr.EventData, counter: int, n_max_videos: int, seen_videos: list
):
    counter += 1
    if counter <= n_max_videos:
        index = event._data.get("index")
        seen_videos.append(index)
        video_update = gr.update(value=video_files[index], visible=True, autoplay=True)
        tabs_update = gr.update(selected=1)
    else:
        counter = n_max_videos
        video_update = gr.update(value=None, visible=False, autoplay=False)
        tabs_update = gr.update(selected=0)
    return counter, video_update, tabs_update, seen_videos


def compute_time_passed_f(start_time: datetime.datetime):
    dt = now() - start_time
    m = int(dt.total_seconds() // 60)
    s = int(dt.total_seconds() % 60)
    # Format the output with leading zeros for minutes and seconds if needed
    output = f"{m}:{s:02d}" if s < 10 else f"{m}:{s}"
    return output


def end_video(video: str, counter: int, n_max_videos: int):
    video = gr.update(value=None, visible=False, autoplay=False)
    if counter < n_max_videos - 1:
        tab_update = gr.update(selected=1)
        info_update = None
    elif counter == n_max_videos - 1:
        tab_update = gr.update(selected=0)
        info_update = gr.update(
            value="data/one_more.mp4", interactive=False, visible=True, autoplay=True
        )
    else:
        tab_update = gr.update(selected=0)
        info_update = gr.update(
            value="data/finished.mp4", interactive=False, visible=True, autoplay=True
        )
    return video, tab_update, info_update


# %%

css = """
.info textarea {font-size: 3em; !important}
"""

with gr.Blocks(css=css) as demo:
    # State
    st_counter = gr.State(value=0)
    st_start = gr.State(value=now())
    st_n_max_videos = gr.State(value=n_max_videos)
    st_seen_videos = gr.State(value=[])

    # Layout
    gr.Markdown("## MyTube")
    gr.Markdown("Developed by Mauricio Fernández")
    with gr.Row():
        with gr.Column(scale=4):
            with gr.Tabs() as tabs:
                with gr.Tab(label="Video", id=1):
                    video = gr.Video(value=None, scale=3, autoplay=True, visible=False)
                with gr.Tab(label="Info", id=0):
                    info_video = gr.Video(None, visible=False)
        with gr.Column(scale=1):
            display_counter = gr.Textbox(
                st_counter.value, label="Counter", elem_classes="info"
            )
            thumbnail_gallery = gr.Gallery(
                thumbnails, label="Thumbnails", allow_preview=False, columns=2
            )
    display_start = gr.Textbox(
        st_start.value.strftime("%Y-%m-%d %H:%M"), label="Start Time"
    )
    display_seen_videos = gr.Gallery(
        None, label="Seen videos", interactive=False, columns=st_n_max_videos.value
    )
    with gr.Accordion(label="Parental control", open=False):
        with gr.Row():
            compute_time_passed = gr.Button(value="Compute time passed")
            display_time_passed = gr.Textbox(
                label="Time passed (minutes:seconds)", value="0:00"
            )
        parental_max_videos = gr.Radio(
            choices=[4, 5, 6, 7, 8], value=4, label="Max videos"
        )

    # Bindings
    video.end(
        fn=end_video,
        inputs=[video, st_counter, st_n_max_videos],
        outputs=[video, tabs, info_video],
    )
    thumbnail_gallery.select(
        fn=select_thumbnail,
        inputs=[st_counter, st_n_max_videos, st_seen_videos],
        outputs=[st_counter, video, tabs, st_seen_videos],
    ).then(
        fn=lambda x: x,
        inputs=st_counter,
        outputs=display_counter,
    ).then(
        fn=lambda x: gr.update(
            value=[thumbnails[i] for i in x], columns=st_n_max_videos.value
        ),
        inputs=st_seen_videos,
        outputs=display_seen_videos,
    ).then(
        fn=lambda: None,
        inputs=None,
        outputs=thumbnail_gallery,
    ).then(
        fn=lambda: thumbnails,
        inputs=None,
        outputs=thumbnail_gallery,
    )
    compute_time_passed.click(
        fn=compute_time_passed_f,
        inputs=st_start,
        outputs=display_time_passed,
    )
    parental_max_videos.select(
        fn=lambda x: x,
        inputs=parental_max_videos,
        outputs=st_n_max_videos,
    )

demo.launch(inbrowser=True)
