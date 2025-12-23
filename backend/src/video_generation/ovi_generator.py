import os
import sys
import tempfile
from typing import Optional, List, Callable
from dataclasses import dataclass
from pathlib import Path

from ..prompt_generation.prompt_generator import VideoPrompt


@dataclass
class GeneratedClip:
    segment_index: int
    start_time: float
    end_time: float
    video_path: str
    prompt_used: str


@dataclass
class GenerationConfig:
    model_name: str = "960x960_10s"
    video_height: int = 960
    video_width: int = 960
    sample_steps: int = 50
    video_guidance_scale: float = 4.0
    audio_guidance_scale: float = 3.0
    cpu_offload: bool = True
    fp8: bool = False
    seed: int = 100


class OviVideoGenerator:
    def __init__(
        self,
        ovi_path: str = "./Ovi",
        config: Optional[GenerationConfig] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ):
        self.ovi_path = Path(ovi_path)
        self.config = config or GenerationConfig()
        self.progress_callback = progress_callback
        self._engine = None
        self._initialized = False

    def initialize(self):
        if self._initialized:
            return

        ovi_path_str = str(self.ovi_path)
        if ovi_path_str not in sys.path:
            sys.path.insert(0, ovi_path_str)

        try:
            from ovi.ovi_fusion_engine import OviFusionEngine, DEFAULT_CONFIG

            DEFAULT_CONFIG["cpu_offload"] = self.config.cpu_offload
            DEFAULT_CONFIG["fp8"] = self.config.fp8
            DEFAULT_CONFIG["model_name"] = self.config.model_name
            DEFAULT_CONFIG["mode"] = "t2v"

            self._engine = OviFusionEngine()
            self._initialized = True
        except ImportError as e:
            raise ImportError(
                f"Failed to import Ovi. Make sure Ovi is cloned to {self.ovi_path}. "
                f"Error: {e}"
            )

    def generate_clips(
        self,
        prompts: List[VideoPrompt],
        output_dir: str,
        seed: Optional[int] = None
    ) -> List[GeneratedClip]:
        if not self._initialized:
            self.initialize()

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        clips = []
        total = len(prompts)

        for idx, prompt in enumerate(prompts):
            if self.progress_callback:
                self.progress_callback(idx + 1, total, f"Generating clip {idx + 1}/{total}")

            clip = self._generate_single_clip(
                prompt=prompt,
                output_dir=output_path,
                seed=seed or self.config.seed
            )
            clips.append(clip)

        return clips

    def _generate_single_clip(
        self,
        prompt: VideoPrompt,
        output_dir: Path,
        seed: int
    ) -> GeneratedClip:
        from ovi.utils.io_utils import save_video

        ovi_prompt = self._format_prompt_for_ovi(prompt)

        generated_video, generated_audio, _ = self._engine.generate(
            text_prompt=ovi_prompt,
            image_path=None,
            video_frame_height_width=[self.config.video_height, self.config.video_width],
            seed=seed + prompt.segment_index,
            solver_name="unipc",
            sample_steps=self.config.sample_steps,
            shift=5.0,
            video_guidance_scale=self.config.video_guidance_scale,
            audio_guidance_scale=self.config.audio_guidance_scale,
            slg_layer=11,
            video_negative_prompt=prompt.negative_prompt,
            audio_negative_prompt="robotic, muffled, echo, distorted"
        )

        output_filename = f"clip_{prompt.segment_index:04d}.mp4"
        output_path = output_dir / output_filename

        save_video(str(output_path), generated_video, generated_audio, fps=24, sample_rate=16000)

        return GeneratedClip(
            segment_index=prompt.segment_index,
            start_time=prompt.start_time,
            end_time=prompt.end_time,
            video_path=str(output_path),
            prompt_used=ovi_prompt
        )

    def _format_prompt_for_ovi(self, prompt: VideoPrompt) -> str:
        return f"{prompt.prompt_text}\n\n{prompt.audio_description}"

    def generate_single(
        self,
        prompt_text: str,
        audio_description: str,
        output_path: str,
        negative_prompt: str = "",
        seed: Optional[int] = None
    ) -> str:
        if not self._initialized:
            self.initialize()

        from ovi.utils.io_utils import save_video

        full_prompt = f"{prompt_text}\n\nAudio: {audio_description}"

        generated_video, generated_audio, _ = self._engine.generate(
            text_prompt=full_prompt,
            image_path=None,
            video_frame_height_width=[self.config.video_height, self.config.video_width],
            seed=seed or self.config.seed,
            solver_name="unipc",
            sample_steps=self.config.sample_steps,
            shift=5.0,
            video_guidance_scale=self.config.video_guidance_scale,
            audio_guidance_scale=self.config.audio_guidance_scale,
            slg_layer=11,
            video_negative_prompt=negative_prompt,
            audio_negative_prompt="robotic, muffled, echo, distorted"
        )

        save_video(output_path, generated_video, generated_audio, fps=24, sample_rate=16000)

        return output_path

    def is_available(self) -> bool:
        try:
            self.initialize()
            return True
        except (ImportError, Exception):
            return False


class MockOviVideoGenerator(OviVideoGenerator):
    def initialize(self):
        self._initialized = True

    def _generate_single_clip(
        self,
        prompt: VideoPrompt,
        output_dir: Path,
        seed: int
    ) -> GeneratedClip:
        import cv2
        import numpy as np

        output_filename = f"clip_{prompt.segment_index:04d}.mp4"
        output_path = output_dir / output_filename

        duration = prompt.end_time - prompt.start_time
        fps = 24
        num_frames = int(duration * fps)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(
            str(output_path),
            fourcc,
            fps,
            (self.config.video_width, self.config.video_height)
        )

        for i in range(num_frames):
            frame = np.zeros((self.config.video_height, self.config.video_width, 3), dtype=np.uint8)

            hue = int((i / num_frames) * 180)
            frame[:, :] = [hue, 200, 200]
            frame = cv2.cvtColor(frame, cv2.COLOR_HSV2BGR)

            font = cv2.FONT_HERSHEY_SIMPLEX
            text = f"Segment {prompt.segment_index}"
            cv2.putText(frame, text, (50, 100), font, 2, (255, 255, 255), 3)

            out.write(frame)

        out.release()

        return GeneratedClip(
            segment_index=prompt.segment_index,
            start_time=prompt.start_time,
            end_time=prompt.end_time,
            video_path=str(output_path),
            prompt_used=prompt.prompt_text
        )
