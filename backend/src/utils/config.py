import os
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path


@dataclass
class Config:
    ovi_path: str = "../Ovi"
    output_dir: str = "./output"
    temp_dir: str = "./temp"

    video_width: int = 720
    video_height: int = 720
    video_fps: int = 24
    segment_duration: float = 5.0

    model_name: str = "720x720_5s"
    sample_steps: int = 50
    video_guidance_scale: float = 4.0
    audio_guidance_scale: float = 3.0
    cpu_offload: bool = True
    fp8: bool = True

    whisper_model: str = "base"
    extract_lyrics: bool = True

    crossfade_duration: float = 0.5
    output_video_codec: str = "libx264"
    output_audio_codec: str = "aac"
    output_video_bitrate: str = "8M"
    output_audio_bitrate: str = "192k"

    api_host: str = "127.0.0.1"
    api_port: int = 5000
    debug: bool = False

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            ovi_path=os.getenv("OVI_PATH", "../Ovi"),
            output_dir=os.getenv("OUTPUT_DIR", "./output"),
            temp_dir=os.getenv("TEMP_DIR", "./temp"),
            video_width=int(os.getenv("VIDEO_WIDTH", "720")),
            video_height=int(os.getenv("VIDEO_HEIGHT", "720")),
            segment_duration=float(os.getenv("SEGMENT_DURATION", "5.0")),
            model_name=os.getenv("MODEL_NAME", "720x720_5s"),
            sample_steps=int(os.getenv("SAMPLE_STEPS", "50")),
            cpu_offload=os.getenv("CPU_OFFLOAD", "true").lower() == "true",
            fp8=os.getenv("FP8", "true").lower() == "true",
            whisper_model=os.getenv("WHISPER_MODEL", "base"),
            extract_lyrics=os.getenv("EXTRACT_LYRICS", "true").lower() == "true",
            api_host=os.getenv("API_HOST", "127.0.0.1"),
            api_port=int(os.getenv("API_PORT", "5000")),
            debug=os.getenv("DEBUG", "false").lower() == "true"
        )

    def ensure_directories(self):
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.temp_dir).mkdir(parents=True, exist_ok=True)

    def to_dict(self) -> dict:
        return {
            "ovi_path": self.ovi_path,
            "output_dir": self.output_dir,
            "temp_dir": self.temp_dir,
            "video_width": self.video_width,
            "video_height": self.video_height,
            "video_fps": self.video_fps,
            "segment_duration": self.segment_duration,
            "model_name": self.model_name,
            "sample_steps": self.sample_steps,
            "video_guidance_scale": self.video_guidance_scale,
            "audio_guidance_scale": self.audio_guidance_scale,
            "cpu_offload": self.cpu_offload,
            "fp8": self.fp8,
            "whisper_model": self.whisper_model,
            "extract_lyrics": self.extract_lyrics,
            "crossfade_duration": self.crossfade_duration,
            "api_host": self.api_host,
            "api_port": self.api_port,
            "debug": self.debug
        }
