import os
import tempfile
from typing import List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
import subprocess

from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    concatenate_videoclips,
    CompositeVideoClip,
    ColorClip
)

from .ovi_generator import GeneratedClip


@dataclass
class CompositionConfig:
    output_resolution: Tuple[int, int] = (1920, 1080)
    output_fps: int = 24
    crossfade_duration: float = 0.5
    audio_fade_in: float = 0.1
    audio_fade_out: float = 0.5
    video_codec: str = "libx264"
    audio_codec: str = "aac"
    video_bitrate: str = "8M"
    audio_bitrate: str = "192k"


class VideoComposer:
    def __init__(self, config: Optional[CompositionConfig] = None):
        self.config = config or CompositionConfig()

    def compose_music_video(
        self,
        clips: List[GeneratedClip],
        original_audio_path: str,
        output_path: str,
        use_crossfade: bool = True
    ) -> str:
        clips_sorted = sorted(clips, key=lambda c: c.segment_index)

        video_clips = []
        for clip in clips_sorted:
            if not os.path.exists(clip.video_path):
                raise FileNotFoundError(f"Video clip not found: {clip.video_path}")

            video = VideoFileClip(clip.video_path)
            video_clips.append(video)

        if use_crossfade and len(video_clips) > 1:
            final_video = self._concatenate_with_crossfade(video_clips)
        else:
            final_video = concatenate_videoclips(video_clips, method="compose")

        original_audio = AudioFileClip(original_audio_path)

        if final_video.duration < original_audio.duration:
            final_video = self._extend_video_to_audio(final_video, original_audio.duration)
        elif final_video.duration > original_audio.duration:
            final_video = final_video.subclip(0, original_audio.duration)

        original_audio = original_audio.audio_fadein(self.config.audio_fade_in)
        original_audio = original_audio.audio_fadeout(self.config.audio_fade_out)

        final_video = final_video.set_audio(original_audio)

        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        final_video.write_videofile(
            output_path,
            fps=self.config.output_fps,
            codec=self.config.video_codec,
            audio_codec=self.config.audio_codec,
            bitrate=self.config.video_bitrate,
            audio_bitrate=self.config.audio_bitrate,
            threads=4,
            preset='medium'
        )

        for clip in video_clips:
            clip.close()
        final_video.close()
        original_audio.close()

        return output_path

    def _concatenate_with_crossfade(self, clips: List[VideoFileClip]) -> VideoFileClip:
        if len(clips) == 1:
            return clips[0]

        crossfade = self.config.crossfade_duration

        result = clips[0]
        for i in range(1, len(clips)):
            current_clip = clips[i]

            if result.duration > crossfade:
                result = concatenate_videoclips(
                    [result, current_clip],
                    method="compose",
                    padding=-crossfade
                )
            else:
                result = concatenate_videoclips([result, current_clip], method="compose")

        return result

    def _extend_video_to_audio(
        self,
        video: VideoFileClip,
        target_duration: float
    ) -> VideoFileClip:
        if video.duration >= target_duration:
            return video

        loops_needed = int(target_duration / video.duration) + 1
        extended_clips = [video] * loops_needed
        extended = concatenate_videoclips(extended_clips, method="compose")
        return extended.subclip(0, target_duration)

    def replace_audio(
        self,
        video_path: str,
        audio_path: str,
        output_path: str
    ) -> str:
        video = VideoFileClip(video_path)
        audio = AudioFileClip(audio_path)

        if video.duration > audio.duration:
            video = video.subclip(0, audio.duration)
        elif audio.duration > video.duration:
            audio = audio.subclip(0, video.duration)

        final = video.set_audio(audio)

        final.write_videofile(
            output_path,
            fps=self.config.output_fps,
            codec=self.config.video_codec,
            audio_codec=self.config.audio_codec,
            bitrate=self.config.video_bitrate,
            audio_bitrate=self.config.audio_bitrate
        )

        video.close()
        audio.close()
        final.close()

        return output_path

    def add_beat_sync_effects(
        self,
        video_path: str,
        beat_times: List[float],
        output_path: str,
        effect_type: str = "flash"
    ) -> str:
        video = VideoFileClip(video_path)

        if effect_type == "flash":
            from moviepy.video.fx.all import colorx

            def apply_flash(get_frame, t):
                frame = get_frame(t)
                for beat_time in beat_times:
                    if abs(t - beat_time) < 0.05:
                        return frame * 1.3

                return frame

            video = video.fl(apply_flash)

        video.write_videofile(output_path)
        video.close()

        return output_path

    def create_preview(
        self,
        video_path: str,
        output_path: str,
        duration: float = 10.0
    ) -> str:
        video = VideoFileClip(video_path)

        preview_duration = min(duration, video.duration)
        preview = video.subclip(0, preview_duration)

        preview.write_videofile(
            output_path,
            fps=self.config.output_fps,
            codec=self.config.video_codec
        )

        video.close()
        preview.close()

        return output_path
