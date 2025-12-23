import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Callable, List
from dataclasses import dataclass, field


@dataclass
class LipSyncConfig:
    musetalk_path: str = ""
    version: str = "v15"
    use_float16: bool = True
    fps: int = 25
    batch_size: int = 8
    bbox_shift: int = 0

    def __post_init__(self):
        if not self.musetalk_path:
            project_root = Path(__file__).parent.parent.parent.parent
            self.musetalk_path = str(project_root / "MuseTalk")


class MuseTalkLipSyncProcessor:
    def __init__(
        self,
        config: Optional[LipSyncConfig] = None,
        progress_callback: Optional[Callable[[str], None]] = None
    ):
        self.config = config or LipSyncConfig()
        self.progress_callback = progress_callback
        self.musetalk_path = Path(self.config.musetalk_path)
        self._initialized = False

    def _log(self, message: str):
        if self.progress_callback:
            self.progress_callback(message)
        print(f"[LipSync] {message}")

    def _verify_installation(self) -> bool:
        required_files = [
            "models/musetalkV15/unet.pth",
            "models/musetalkV15/musetalk.json",
            "models/sd-vae/diffusion_pytorch_model.bin",
            "models/whisper/pytorch_model.bin",
            "models/dwpose/dw-ll_ucoco_384.pth",
            "models/face-parse-bisent/79999_iter.pth",
        ]

        for file in required_files:
            if not (self.musetalk_path / file).exists():
                self._log(f"Missing required file: {file}")
                return False

        return True

    def initialize(self) -> bool:
        if self._initialized:
            return True

        self._log("Initializing MuseTalk lip sync processor...")

        if not self.musetalk_path.exists():
            self._log(f"MuseTalk not found at {self.musetalk_path}")
            return False

        if not self._verify_installation():
            self._log("MuseTalk installation incomplete. Run download_weights.sh")
            return False

        self._initialized = True
        self._log("MuseTalk initialized successfully")
        return True

    def process_video(
        self,
        input_video_path: str,
        audio_path: str,
        output_path: str
    ) -> str:
        if not self.initialize():
            raise RuntimeError("MuseTalk initialization failed")

        self._log(f"Processing: {Path(input_video_path).name}")

        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        temp_config = self._create_temp_config(input_video_path, audio_path)

        try:
            cmd = [
                sys.executable, "-m", "scripts.inference",
                "--inference_config", str(temp_config),
                "--result_dir", str(output_dir),
            ]

            if self.config.use_float16:
                cmd.append("--use_float16")

            if self.config.bbox_shift != 0:
                cmd.extend(["--bbox_shift", str(self.config.bbox_shift)])

            env = os.environ.copy()
            env["PYTHONPATH"] = str(self.musetalk_path)

            self._log(f"Running MuseTalk inference...")
            result = subprocess.run(
                cmd,
                cwd=str(self.musetalk_path),
                env=env,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                self._log(f"MuseTalk error: {result.stderr}")
                raise RuntimeError(f"MuseTalk inference failed: {result.stderr}")

            generated_file = self._find_output_file(output_dir)
            if generated_file and generated_file != output_path:
                shutil.move(str(generated_file), output_path)

            self._log(f"Lip sync complete: {output_path}")
            return output_path

        finally:
            if temp_config.exists():
                temp_config.unlink()

    def _create_temp_config(self, video_path: str, audio_path: str) -> Path:
        import yaml

        config_content = {
            "task_0": {
                "video_path": str(video_path),
                "audio_path": str(audio_path),
            }
        }

        temp_config = self.musetalk_path / "configs" / "inference" / f"temp_{os.getpid()}.yaml"
        with open(temp_config, "w") as f:
            yaml.dump(config_content, f)

        return temp_config

    def _find_output_file(self, output_dir: Path) -> Optional[Path]:
        mp4_files = list(output_dir.glob("*.mp4"))
        if mp4_files:
            return sorted(mp4_files, key=lambda x: x.stat().st_mtime, reverse=True)[0]
        return None

    def process_clips_batch(
        self,
        video_paths: List[str],
        audio_segments: List[str],
        output_dir: str
    ) -> List[str]:
        if len(video_paths) != len(audio_segments):
            raise ValueError("Number of videos must match number of audio segments")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        synced_clips = []
        total = len(video_paths)

        for idx, (video_path, audio_path) in enumerate(zip(video_paths, audio_segments)):
            self._log(f"Processing clip {idx + 1}/{total}")

            output_filename = f"synced_{Path(video_path).name}"
            output_file = output_path / output_filename

            try:
                self.process_video(
                    input_video_path=video_path,
                    audio_path=audio_path,
                    output_path=str(output_file)
                )
                synced_clips.append(str(output_file))
            except Exception as e:
                self._log(f"Failed to process clip {idx + 1}: {e}")
                synced_clips.append(video_path)

        return synced_clips


def create_audio_segment(
    audio_path: str,
    start_time: float,
    duration: float,
    output_path: str
) -> str:
    cmd = [
        "ffmpeg", "-y",
        "-i", audio_path,
        "-ss", str(start_time),
        "-t", str(duration),
        "-acodec", "copy",
        output_path
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    return output_path
