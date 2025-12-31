# %%

import datetime
import glob
import json
import os

import gradio as gr
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
        self.video_files = sorted(glob.glob(f"{self.processed_videos_folder}/*.mp4"))
        self.thumbnail_folder = os.path.join(self.processed_videos_folder, "thumbnails")
        self.thumbnails = self._get_thumbnails()
        self.color_done = color_done
        self.color_undone = color_undone
        self.state_file = os.path.abspath("webapp_state.json")
        print(f"WebApp state file: {self.state_file}")
        self._write_state(self._default_state())
        self.state = self._load_state()

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

    def _default_state(self):
        return {
            "counter": 0,
            "seen_videos": [],
            "n_max_videos": self.n_max_videos,
        }

    def _load_state(self):
        if not os.path.exists(self.state_file):
            state = self._default_state()
            self._write_state(state)
            return state
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
        except (json.JSONDecodeError, OSError):
            state = self._default_state()
        stored_limit = state.get("n_max_videos", self.n_max_videos)
        try:
            stored_limit = int(stored_limit)
        except (TypeError, ValueError):
            stored_limit = self.n_max_videos
        if stored_limit > 0:
            self.n_max_videos = stored_limit
        counter = int(state.get("counter", 0))
        counter = max(0, min(counter, self.n_max_videos))
        raw_seen = state.get("seen_videos", [])
        seen_videos = []
        for candidate in raw_seen:
            try:
                idx = int(candidate)
            except (TypeError, ValueError):
                continue
            if 0 <= idx < len(self.thumbnails):
                seen_videos.append(idx)
        if len(seen_videos) > counter:
            seen_videos = seen_videos[:counter]
        clean_state = {
            "counter": counter,
            "seen_videos": seen_videos,
            "n_max_videos": self.n_max_videos,
        }
        self._write_state(clean_state)
        return clean_state

    def _write_state(self, state):
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(state, f)
        except OSError:
            pass
        else:
            self.state = state

    def _prepare_state_payload(self):
        state = self._load_state()
        counter = int(state.get("counter", 0))
        try:
            limit = int(state.get("n_max_videos", self.n_max_videos))
        except (TypeError, ValueError):
            limit = self.n_max_videos
        if limit <= 0:
            limit = max(1, self.n_max_videos)
        self.n_max_videos = limit
        counter = max(0, min(counter, limit))
        raw_seen = state.get("seen_videos", [])
        seen_videos = []
        for candidate in raw_seen:
            try:
                idx = int(candidate)
            except (TypeError, ValueError):
                continue
            if 0 <= idx < len(self.thumbnails):
                seen_videos.append(idx)
        if len(seen_videos) > counter:
            seen_videos = seen_videos[:counter]
        thumbnails_seen = [self.thumbnails[i] for i in seen_videos]
        gallery_columns = limit if limit > 0 else 1
        progress_plot = self.gen_progress_plot(limit, counter)
        display_max_value = str(limit)
        radio_choices = {4, 5, 6, 7, 8}
        radio_value = limit if limit in radio_choices else min(max(limit, 4), 8)
        return (
            counter,
            limit,
            seen_videos,
            str(counter),
            gr.update(value=thumbnails_seen or None, columns=gallery_columns),
            progress_plot,
            display_max_value,
            gr.update(value=radio_value),
        )

    def _save_state(self, counter, seen_videos, n_max_videos=None):
        limit = n_max_videos if n_max_videos is not None else self.n_max_videos
        try:
            limit = int(limit)
        except (TypeError, ValueError):
            limit = self.n_max_videos
        if limit > 0:
            self.n_max_videos = limit
        cleaned_seen = []
        for candidate in seen_videos:
            try:
                idx = int(candidate)
            except (TypeError, ValueError):
                continue
            if 0 <= idx < len(self.thumbnails):
                cleaned_seen.append(idx)
        state = {
            "counter": max(0, min(int(counter), self.n_max_videos)),
            "seen_videos": cleaned_seen,
            "n_max_videos": self.n_max_videos,
        }
        self._write_state(state)

    def check_video_counter(self, counter: int, video: str, n_max_videos: int):
        if counter > n_max_videos:
            return gr.update(value=None, interactive=False), n_max_videos
        else:
            return gr.update(value=video), counter

    def select_thumbnail(
        self, event: gr.EventData, counter: int, n_max_videos: int, seen_videos: list
    ):
        try:
            current_limit = int(n_max_videos)
        except (TypeError, ValueError):
            current_limit = self.n_max_videos
        if current_limit <= 0:
            current_limit = max(1, self.n_max_videos)
        seen_videos = list(seen_videos or [])
        counter += 1
        if counter <= current_limit:
            raw_index = event._data.get("index")
            try:
                idx = int(raw_index)
            except (TypeError, ValueError):
                idx = None
            if idx is not None and 0 <= idx < len(self.video_files):
                seen_videos.append(idx)
                video_update = gr.update(
                    value=self.video_files[idx], visible=True, autoplay=True
                )
                tabs_update = gr.update(selected=1)
            else:
                counter -= 1
                video_update = gr.update(value=None, visible=False, autoplay=False)
                tabs_update = gr.update(selected=0)
        else:
            counter = current_limit
            video_update = gr.update(value=None, visible=False, autoplay=False)
            tabs_update = gr.update(selected=0)
        progress_plot = self.gen_progress_plot(current_limit, counter)
        self._save_state(counter, seen_videos, current_limit)

        # Force the browser video element to fully reset before loading the next
        # source to avoid getting stuck in the "loading" overlay while audio plays.
        yield (
            counter,
            gr.update(value=None, visible=True, autoplay=False),
            tabs_update,
            seen_videos,
            progress_plot,
        )
        yield counter, video_update, tabs_update, seen_videos, progress_plot

    def compute_time_passed_f(self, start_time: datetime.datetime):
        dt = now() - start_time
        m = int(dt.total_seconds() // 60)
        s = int(dt.total_seconds() % 60)
        output = f"{m}:{s:02d}" if s < 10 else f"{m}:{s}"
        return output

    def end_video(self, video: str, counter: int, n_max_videos: int):
        # Always clear the player first so re-playing the same info video works after undo.
        video_clear = gr.update(value=None, visible=True, autoplay=False)

        if counter < n_max_videos - 1:
            tab_update = gr.update(selected=2)
            info_steps = [gr.update(value=None, visible=True, autoplay=False)]
        elif counter == n_max_videos - 1:
            tab_update = gr.update(selected=0)
            if os.path.exists(self.only_one_more_path):
                info_steps = [
                    gr.update(value=None, visible=True, autoplay=False),
                    gr.update(
                        value=self.only_one_more_path,
                        interactive=False,
                        visible=True,
                        autoplay=True,
                    ),
                ]
            else:
                info_steps = [gr.update(value=None, visible=True, autoplay=False)]
        else:
            tab_update = gr.update(selected=0)
            if os.path.exists(self.finished_path):
                info_steps = [
                    gr.update(value=None, visible=True, autoplay=False),
                    gr.update(
                        value=self.finished_path,
                        interactive=False,
                        visible=True,
                        autoplay=True,
                    ),
                ]
            else:
                info_steps = [gr.update(value=None, visible=True, autoplay=False)]

        # Step 1: clear info video to force reload even if the same file is played again.
        yield video_clear, tab_update, info_steps[0]

        # Step 2: play the requested info video when available.
        if len(info_steps) > 1:
            yield video_clear, tab_update, info_steps[1]

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
            wedgeprops=dict(edgecolor="black"),  # Black borders for visibility
        )

        return fig

    def update_max_videos(self, n_max_videos: int, counter: int, seen_videos: list):
        seen_videos = list(seen_videos or [])
        self._save_state(counter, seen_videos, n_max_videos)
        return self._prepare_state_payload()

    def undo_last_video(self, counter: int, seen_videos: list, n_max_videos: int):
        """Remove the most recent selection and roll back counter/state."""
        seen_videos = list(seen_videos or [])
        try:
            limit = int(n_max_videos)
        except (TypeError, ValueError):
            limit = self.n_max_videos
        if limit <= 0:
            limit = max(1, self.n_max_videos)

        if counter > 0:
            counter -= 1
        if seen_videos:
            seen_videos = seen_videos[:-1]

        self._save_state(counter, seen_videos, limit)

        seen_gallery = gr.update(
            value=[self.thumbnails[i] for i in seen_videos] or None,
            columns=limit if limit > 0 else 1,
        )
        progress_plot = self.gen_progress_plot(limit, counter)
        video_update = gr.update(value=None, visible=True, autoplay=False)
        info_update = gr.update(value=None, visible=True, autoplay=False)

        return (
            counter,
            seen_videos,
            str(counter),
            seen_gallery,
            progress_plot,
            video_update,
            info_update,
        )

    def launch(self, server_name="0.0.0.0", server_port=7860, inbrowser=True):
        css = """
        .info textarea {font-size: 2em; !important; color: %s;}
        .info2 textarea {font-size: 2em; color: %s;}
        """ % (
            self.color_done,
            self.color_undone,
        )

        with gr.Blocks() as demo:
            # State
            st_counter = gr.State(value=self.state.get("counter", 0))
            st_start = gr.State(value=now())
            st_n_max_videos = gr.State(value=self.n_max_videos)
            st_seen_videos = gr.State(value=self.state.get("seen_videos", []))
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
                                value=None, scale=3, autoplay=True, visible=True
                            )
                        with gr.Tab(label="Info", id=0):
                            info_video = gr.Video(None, visible=True)
                with gr.Column(scale=1):
                    display_counter = gr.Textbox(
                        str(self.state.get("counter", 0)),
                        label="Counter",
                        elem_classes="info",
                    )
                    display_max = gr.Textbox(
                        str(self.state.get("n_max_videos", self.n_max_videos)),
                        label="Max Videos",
                        interactive=False,
                        elem_classes="info2",
                    )
                    progress_plot = gr.Plot(
                        value=self.gen_progress_plot(
                            self.state.get("n_max_videos", self.n_max_videos),
                            self.state.get("counter", 0),
                        )
                    )
            display_seen_videos = gr.Gallery(
                [
                    self.thumbnails[i]
                    for i in self.state.get("seen_videos", [])
                    if 0 <= i < len(self.thumbnails)
                ]
                or None,
                label="Seen videos",
                interactive=False,
                columns=self.state.get("n_max_videos", self.n_max_videos),
            )
            with gr.Accordion(label="Parental control", open=False):
                display_start = gr.Textbox(
                    st_start.value.strftime("%Y-%m-%d %H:%M"), label="Start Time"
                )
                with gr.Row():
                    compute_time_passed = gr.Button(value="Compute time passed")
                    display_time_passed = gr.Textbox(
                        label="Time passed (minutes:seconds)", value="0:00"
                    )
                undo_last_video_btn = gr.Button("Undo last video")
                parental_max_videos = gr.Radio(
                    choices=[4, 5, 6, 7, 8],
                    value=min(
                        max(self.state.get("n_max_videos", self.n_max_videos), 4),
                        8,
                    ),
                    label="Max videos",
                )

            # Bindings
            demo.load(
                fn=self._prepare_state_payload,
                inputs=None,
                outputs=[
                    st_counter,
                    st_n_max_videos,
                    st_seen_videos,
                    display_counter,
                    display_seen_videos,
                    progress_plot,
                    display_max,
                    parental_max_videos,
                ],
            )

            video.end(
                fn=self.end_video,
                inputs=[video, st_counter, st_n_max_videos],
                outputs=[video, tabs, info_video],
            ).then(
                fn=lambda: gr.update(value=[]),
                inputs=None,
                outputs=thumbnail_gallery,
            ).then(
                fn=lambda: gr.update(value=self.thumbnails),
                inputs=None,
                outputs=thumbnail_gallery,
            )

            info_video.end(
                fn=self.end_info_video,
                inputs=None,
                outputs=[tabs],
            ).then(
                fn=lambda: gr.update(value=[]),
                inputs=None,
                outputs=thumbnail_gallery,
            ).then(
                fn=lambda: gr.update(value=self.thumbnails),
                inputs=None,
                outputs=thumbnail_gallery,
            )

            thumbnail_gallery.select(
                fn=self.select_thumbnail,
                inputs=[st_counter, st_n_max_videos, st_seen_videos],
                outputs=[st_counter, video, tabs, st_seen_videos, progress_plot],
            ).then(
                fn=lambda x: str(x),
                inputs=st_counter,
                outputs=display_counter,
            ).then(
                fn=lambda seen, limit: gr.update(
                    value=[self.thumbnails[i] for i in (seen or [])],
                    columns=limit if limit > 0 else 1,
                ),
                inputs=[st_seen_videos, st_n_max_videos],
                outputs=display_seen_videos,
            )

            compute_time_passed.click(
                fn=self.compute_time_passed_f,
                inputs=st_start,
                outputs=display_time_passed,
            )

            parental_max_videos.select(
                fn=self.update_max_videos,
                inputs=[parental_max_videos, st_counter, st_seen_videos],
                outputs=[
                    st_counter,
                    st_n_max_videos,
                    st_seen_videos,
                    display_counter,
                    display_seen_videos,
                    progress_plot,
                    display_max,
                    parental_max_videos,
                ],
            )

            undo_last_video_btn.click(
                fn=self.undo_last_video,
                inputs=[st_counter, st_seen_videos, st_n_max_videos],
                outputs=[
                    st_counter,
                    st_seen_videos,
                    display_counter,
                    display_seen_videos,
                    progress_plot,
                    video,
                    info_video,
                ],
            )

        demo.launch(
            inbrowser=inbrowser,
            server_name=server_name,
            server_port=server_port,
            css=css,
        )
