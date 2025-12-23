import os
import uuid
import shutil
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
from pathlib import Path
from enum import Enum

from .audio_analysis import AudioAnalyzer
from .prompt_generation import PromptGenerator
from .video_generation import OviVideoGenerator, VideoComposer, MockOviVideoGenerator
from .video_generation.ovi_generator import GenerationConfig
from .video_generation.video_composer import CompositionConfig
from .utils import Config, validate_audio_file, ensure_directory


class PipelineStatus(Enum):
    IDLE = "idle"
    ANALYZING = "analyzing"
    GENERATING_PROMPTS = "generating_prompts"
    GENERATING_VIDEO = "generating_video"
    COMPOSING = "composing"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class PipelineProgress:
    status: PipelineStatus
    progress: float
    message: str
    current_step: int
    total_steps: int


@dataclass
class MusicVideoResult:
    job_id: str
    output_path: str
    duration: float
    segments_generated: int
    analysis_summary: Dict[str, Any]


class MusicVideoPipeline:
    def __init__(
        self,
        config: Optional[Config] = None,
        progress_callback: Optional[Callable[[PipelineProgress], None]] = None,
        use_mock_generator: bool = False
    ):
        self.config = config or Config.from_env()
        self.progress_callback = progress_callback
        self.use_mock_generator = use_mock_generator

        self.config.ensure_directories()

        self.audio_analyzer = AudioAnalyzer(
            segment_duration=self.config.segment_duration
        )

        self.prompt_generator = PromptGenerator()

        gen_config = GenerationConfig(
            model_name=self.config.model_name,
            video_height=self.config.video_height,
            video_width=self.config.video_width,
            sample_steps=self.config.sample_steps,
            video_guidance_scale=self.config.video_guidance_scale,
            audio_guidance_scale=self.config.audio_guidance_scale,
            cpu_offload=self.config.cpu_offload,
            fp8=self.config.fp8
        )

        if use_mock_generator:
            self.video_generator = MockOviVideoGenerator(
                ovi_path=self.config.ovi_path,
                config=gen_config
            )
        else:
            self.video_generator = OviVideoGenerator(
                ovi_path=self.config.ovi_path,
                config=gen_config
            )

        comp_config = CompositionConfig(
            crossfade_duration=self.config.crossfade_duration,
            video_codec=self.config.output_video_codec,
            audio_codec=self.config.output_audio_codec,
            video_bitrate=self.config.output_video_bitrate,
            audio_bitrate=self.config.output_audio_bitrate,
            enable_lipsync=self.config.enable_lipsync
        )

        self.video_composer = VideoComposer(
            config=comp_config,
            progress_callback=lambda msg: self._update_progress(
                self._current_status, 0.85, msg, 4, 4
            )
        )

        self._current_status = PipelineStatus.IDLE

    def _update_progress(
        self,
        status: PipelineStatus,
        progress: float,
        message: str,
        current_step: int,
        total_steps: int
    ):
        self._current_status = status
        if self.progress_callback:
            self.progress_callback(PipelineProgress(
                status=status,
                progress=progress,
                message=message,
                current_step=current_step,
                total_steps=total_steps
            ))

    def generate(
        self,
        audio_path: str,
        output_filename: Optional[str] = None,
        style_override: Optional[str] = None,
        custom_theme: Optional[str] = None,
        extract_lyrics: bool = True
    ) -> MusicVideoResult:
        job_id = str(uuid.uuid4())[:8]

        valid, error = validate_audio_file(audio_path)
        if not valid:
            raise ValueError(f"Invalid audio file: {error}")

        job_temp_dir = os.path.join(self.config.temp_dir, job_id)
        ensure_directory(job_temp_dir)

        try:
            self._update_progress(
                PipelineStatus.ANALYZING, 0.1,
                "Analyzing audio...", 1, 4
            )

            analysis = self.audio_analyzer.analyze(
                audio_path,
                extract_lyrics=extract_lyrics
            )

            self._update_progress(
                PipelineStatus.GENERATING_PROMPTS, 0.2,
                "Generating visual prompts...", 2, 4
            )

            prompts = self.prompt_generator.generate_prompts(
                analysis,
                style_override=style_override,
                custom_theme=custom_theme
            )

            self._update_progress(
                PipelineStatus.GENERATING_VIDEO, 0.3,
                "Generating video clips...", 3, 4
            )

            def video_progress(current, total, msg):
                progress = 0.3 + (current / total) * 0.5
                self._update_progress(
                    PipelineStatus.GENERATING_VIDEO, progress,
                    msg, 3, 4
                )

            self.video_generator.progress_callback = video_progress

            clips = self.video_generator.generate_clips(
                prompts,
                output_dir=job_temp_dir
            )

            self._update_progress(
                PipelineStatus.COMPOSING, 0.85,
                "Composing final video...", 4, 4
            )

            if output_filename:
                output_path = os.path.join(self.config.output_dir, output_filename)
            else:
                audio_name = Path(audio_path).stem
                output_path = os.path.join(
                    self.config.output_dir,
                    f"{audio_name}_musicvideo_{job_id}.mp4"
                )

            self.video_composer.compose_music_video(
                clips=clips,
                original_audio_path=audio_path,
                output_path=output_path,
                use_crossfade=True
            )

            self._update_progress(
                PipelineStatus.COMPLETED, 1.0,
                "Music video generated successfully!", 4, 4
            )

            analysis_summary = {
                "duration": analysis.duration,
                "tempo": analysis.overall_tempo,
                "mood": analysis.overall_mood,
                "genre": analysis.genre_prediction,
                "segments": len(analysis.segments),
                "has_lyrics": analysis.lyrics is not None
            }

            return MusicVideoResult(
                job_id=job_id,
                output_path=output_path,
                duration=analysis.duration,
                segments_generated=len(clips),
                analysis_summary=analysis_summary
            )

        except Exception as e:
            self._update_progress(
                PipelineStatus.ERROR, 0.0,
                f"Error: {str(e)}", 0, 4
            )
            raise

        finally:
            if os.path.exists(job_temp_dir):
                shutil.rmtree(job_temp_dir, ignore_errors=True)

    def analyze_only(self, audio_path: str) -> Dict[str, Any]:
        valid, error = validate_audio_file(audio_path)
        if not valid:
            raise ValueError(f"Invalid audio file: {error}")

        analysis = self.audio_analyzer.analyze(audio_path, extract_lyrics=True)

        return {
            "duration": analysis.duration,
            "tempo": analysis.overall_tempo,
            "mood": analysis.overall_mood,
            "genre": analysis.genre_prediction,
            "segments": [
                {
                    "start_time": seg.start_time,
                    "end_time": seg.end_time,
                    "tempo": seg.tempo,
                    "energy": seg.energy,
                    "mood": seg.mood,
                    "lyrics": seg.lyrics
                }
                for seg in analysis.segments
            ],
            "lyrics": analysis.lyrics,
            "beat_count": len(analysis.beat_times)
        }

    def preview_prompts(
        self,
        audio_path: str,
        style_override: Optional[str] = None,
        custom_theme: Optional[str] = None
    ) -> list:
        valid, error = validate_audio_file(audio_path)
        if not valid:
            raise ValueError(f"Invalid audio file: {error}")

        analysis = self.audio_analyzer.analyze(audio_path, extract_lyrics=True)
        prompts = self.prompt_generator.generate_prompts(
            analysis,
            style_override=style_override,
            custom_theme=custom_theme
        )

        return [
            {
                "segment_index": p.segment_index,
                "start_time": p.start_time,
                "end_time": p.end_time,
                "prompt_text": p.prompt_text,
                "audio_description": p.audio_description,
                "negative_prompt": p.negative_prompt
            }
            for p in prompts
        ]

    @property
    def status(self) -> PipelineStatus:
        return self._current_status
