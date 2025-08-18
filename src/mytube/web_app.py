# %%

import gradio as gr
import glob
import os
import datetime
import matplotlib.pyplot as plt

now = datetime.datetime.now

# %%


class WebApp:
    def __init__(
        self,
        title: str = "MyTube",
        information: str = None,
        processed_videos_folder: str = "videos/processed",
        n_max_videos: int = 4,
        only_one_more_path="videos/info/one_more.mp4",
        finished_path="videos/info/finished.mp4",
        color_done="#fca903",
        color_undone="#03fcdf",
    ):
        self.title = title
        self.information = information
        self.processed_videos_folder = processed_videos_folder
        self.n_max_videos = n_max_videos
        self.only_one_more_path = only_one_more_path
        self.finished_path = finished_path
        self.video_files = glob.glob(f"{self.processed_videos_folder}/*.mp4")
        self.thumbnail_folder = os.path.join(self.processed_videos_folder, "thumbnails")
        self.thumbnails = self._get_thumbnails()
        self.color_done = color_done
        self.color_undone = color_undone

    def _get_thumbnails(self):
        thumbnails = []
        for video in self.video_files:
            thumbnail_name = os.path.basename(video).replace(".mp4", ".png")
            thumbnail_path = os.path.join(self.thumbnail_folder, thumbnail_name)
            if os.path.exists(thumbnail_path):
                thumbnails.append(thumbnail_path)
            else:
                self.video_files.remove(video)
        return thumbnails

    def check_video_counter(self, counter: int, video: str, n_max_videos: int):
        if counter > n_max_videos:
            return gr.update(value=None, interactive=False), n_max_videos
        else:
            return gr.update(value=video), counter

    def select_thumbnail(
        self, event: gr.EventData, counter: int, n_max_videos: int, seen_videos: list
    ):
        counter += 1
        if counter <= n_max_videos:
            index = event._data.get("index")
            seen_videos.append(index)
            video_update = gr.update(
                value=self.video_files[index], visible=True, autoplay=True
            )
            tabs_update = gr.update(selected=1)
        else:
            counter = n_max_videos
            video_update = gr.update(value=None, visible=False, autoplay=False)
            tabs_update = gr.update(selected=0)
        progress_plot = self.gen_progress_plot(n_max_videos, counter)
        return counter, video_update, tabs_update, seen_videos, progress_plot

    def compute_time_passed_f(self, start_time: datetime.datetime):
        dt = now() - start_time
        m = int(dt.total_seconds() // 60)
        s = int(dt.total_seconds() % 60)
        output = f"{m}:{s:02d}" if s < 10 else f"{m}:{s}"
        return output

    def end_video(self, video: str, counter: int, n_max_videos: int):
        video = gr.update(value=None, visible=False, autoplay=False)
        if counter < n_max_videos - 1:
            tab_update = gr.update(selected=2)
            info_update = None
        elif counter == n_max_videos - 1:
            tab_update = gr.update(selected=0)
            if os.path.exists(self.only_one_more_path):
                info_update = gr.update(
                    value=self.only_one_more_path,
                    interactive=False,
                    visible=True,
                    autoplay=True,
                )
            else:
                info_update = None
        else:
            tab_update = gr.update(selected=0)
            if os.path.exists(self.finished_path):
                info_update = gr.update(
                    value=self.finished_path,
                    interactive=False,
                    visible=True,
                    autoplay=True,
                )
            else:
                info_update = None
        return video, tab_update, info_update
    
    def end_info_video(self):
        return gr.update(selected=2)

    def gen_progress_plot(self, n_total: int, n_done: int):
        # Define colors for "done" and "undone" sections
        done_color = self.color_done
        undone_color = self.color_undone
        colors = [done_color] * n_done + [undone_color] * (n_total - n_done)

        # Define values and labels
        values = [1] * n_total  # Equal slices
        labels = [""] * n_total  # No labels

        # Create the pie chart
        fig, ax = plt.subplots()
        wedges, texts = ax.pie(
            values,
            colors=colors,
            labels=labels,
            wedgeprops=dict(edgecolor="black")  # Black borders for visibility
        )
        
        return fig

    def update_max_videos(self, n_max_videos: int, counter: int):
        progress_plot = self.gen_progress_plot(n_max_videos, counter)
        return n_max_videos, n_max_videos, progress_plot


    def launch(self):
        css = """
        .info textarea {font-size: 2em; !important; color: %s;}
        .info2 textarea {font-size: 2em; color: %s;}
        """ % (self.color_done, self.color_undone)

        with gr.Blocks(css=css) as demo:
            # State
            st_counter = gr.State(value=0)
            st_start = gr.State(value=now())
            st_n_max_videos = gr.State(value=self.n_max_videos)
            st_seen_videos = gr.State(value=[])
            # Layout
            gr.Markdown(f"## {self.title}")
            if self.information:
                gr.Markdown(self.information)
            with gr.Row():
                with gr.Column(scale=4):
                    with gr.Tabs() as tabs:
                        with gr.Tab(label="Collection", id=2):
                            thumbnail_gallery = gr.Gallery(
                                self.thumbnails,
                                label="Thumbnails",
                                allow_preview=False,
                                columns=5,
                            )
                        with gr.Tab(label="Video", id=1):
                            video = gr.Video(
                                value=None, scale=3, autoplay=True, visible=False
                            )
                        with gr.Tab(label="Info", id=0):
                            info_video = gr.Video(None, visible=False)
                with gr.Column(scale=1):
                    display_counter = gr.Textbox(
                        st_counter.value, label="Counter", elem_classes="info"
                    )
                    display_max = gr.Textbox(
                        st_n_max_videos.value, label="Max Videos", interactive=False, elem_classes="info2"
                    )
                    progress_plot = gr.Plot(value=self.gen_progress_plot(st_n_max_videos.value, 0))
            with gr.Accordion(label="Parental control", open=False):
                display_start = gr.Textbox(
                    st_start.value.strftime("%Y-%m-%d %H:%M"), label="Start Time"
                )
                display_seen_videos = gr.Gallery(
                    None,
                    label="Seen videos",
                    interactive=False,
                    columns=st_n_max_videos.value,
                )
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
                fn=self.end_video,
                inputs=[video, st_counter, st_n_max_videos],
                outputs=[video, tabs, info_video],
            )

            info_video.end(
                fn=self.end_info_video,
                inputs=None,
                outputs=[tabs],
            )
            
            thumbnail_gallery.select(
                fn=self.select_thumbnail,
                inputs=[st_counter, st_n_max_videos, st_seen_videos],
                outputs=[st_counter, video, tabs, st_seen_videos, progress_plot],
            ).then(
                fn=lambda x: x,
                inputs=st_counter,
                outputs=display_counter,
            ).then(
                fn=lambda x: gr.update(
                    value=[self.thumbnails[i] for i in x], columns=st_n_max_videos.value
                ),
                inputs=st_seen_videos,
                outputs=display_seen_videos,
            ).then(
                fn=lambda: None,
                inputs=None,
                outputs=thumbnail_gallery,
            ).then(
                fn=lambda: self.thumbnails,
                inputs=None,
                outputs=thumbnail_gallery,
            )

            compute_time_passed.click(
                fn=self.compute_time_passed_f,
                inputs=st_start,
                outputs=display_time_passed,
            )

            parental_max_videos.select(
                fn=self.update_max_videos,
                inputs=[parental_max_videos, st_counter],
                outputs=[st_n_max_videos, display_max, progress_plot],
            )

        demo.launch(inbrowser=True, server_name="0.0.0.0", server_port=7860)
