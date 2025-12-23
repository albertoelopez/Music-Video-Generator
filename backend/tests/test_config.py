import pytest
import os
from pathlib import Path
from unittest.mock import patch

from src.utils.config import Config


class TestConfig:
    def test_initialization_defaults(self):
        config = Config()

        assert config.ovi_path == "./Ovi"
        assert config.output_dir == "./output"
        assert config.temp_dir == "./temp"
        assert config.video_width == 960
        assert config.video_height == 960
        assert config.video_fps == 24
        assert config.segment_duration == 5.0
        assert config.model_name == "960x960_10s"
        assert config.sample_steps == 50
        assert config.video_guidance_scale == 4.0
        assert config.audio_guidance_scale == 3.0
        assert config.cpu_offload is True
        assert config.fp8 is False
        assert config.whisper_model == "base"
        assert config.extract_lyrics is True
        assert config.crossfade_duration == 0.5
        assert config.output_video_codec == "libx264"
        assert config.output_audio_codec == "aac"
        assert config.output_video_bitrate == "8M"
        assert config.output_audio_bitrate == "192k"
        assert config.api_host == "127.0.0.1"
        assert config.api_port == 5000
        assert config.debug is False

    def test_initialization_custom_values(self):
        config = Config(
            ovi_path="/custom/ovi",
            output_dir="/custom/output",
            video_width=1280,
            video_height=720,
            segment_duration=10.0,
            model_name="custom_model",
            sample_steps=100,
            cpu_offload=False,
            debug=True
        )

        assert config.ovi_path == "/custom/ovi"
        assert config.output_dir == "/custom/output"
        assert config.video_width == 1280
        assert config.video_height == 720
        assert config.segment_duration == 10.0
        assert config.model_name == "custom_model"
        assert config.sample_steps == 100
        assert config.cpu_offload is False
        assert config.debug is True

    def test_from_env_defaults(self):
        with patch.dict(os.environ, {}, clear=True):
            config = Config.from_env()

            assert config.ovi_path == "./Ovi"
            assert config.output_dir == "./output"
            assert config.temp_dir == "./temp"
            assert config.video_width == 960
            assert config.video_height == 960
            assert config.model_name == "960x960_10s"

    def test_from_env_custom_values(self):
        env_vars = {
            "OVI_PATH": "/env/ovi",
            "OUTPUT_DIR": "/env/output",
            "TEMP_DIR": "/env/temp",
            "VIDEO_WIDTH": "1920",
            "VIDEO_HEIGHT": "1080",
            "SEGMENT_DURATION": "8.0",
            "MODEL_NAME": "env_model",
            "SAMPLE_STEPS": "75",
            "CPU_OFFLOAD": "false",
            "FP8": "true",
            "WHISPER_MODEL": "large",
            "EXTRACT_LYRICS": "false",
            "API_HOST": "0.0.0.0",
            "API_PORT": "8000",
            "DEBUG": "true"
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = Config.from_env()

            assert config.ovi_path == "/env/ovi"
            assert config.output_dir == "/env/output"
            assert config.temp_dir == "/env/temp"
            assert config.video_width == 1920
            assert config.video_height == 1080
            assert config.segment_duration == 8.0
            assert config.model_name == "env_model"
            assert config.sample_steps == 75
            assert config.cpu_offload is False
            assert config.fp8 is True
            assert config.whisper_model == "large"
            assert config.extract_lyrics is False
            assert config.api_host == "0.0.0.0"
            assert config.api_port == 8000
            assert config.debug is True

    def test_from_env_boolean_parsing_true(self):
        with patch.dict(os.environ, {"CPU_OFFLOAD": "true", "DEBUG": "TRUE"}, clear=True):
            config = Config.from_env()

            assert config.cpu_offload is True
            assert config.debug is True

    def test_from_env_boolean_parsing_false(self):
        with patch.dict(os.environ, {"CPU_OFFLOAD": "false", "DEBUG": "FALSE"}, clear=True):
            config = Config.from_env()

            assert config.cpu_offload is False
            assert config.debug is False

    def test_from_env_boolean_parsing_case_insensitive(self):
        with patch.dict(os.environ, {"CPU_OFFLOAD": "TrUe", "DEBUG": "FaLsE"}, clear=True):
            config = Config.from_env()

            assert config.cpu_offload is True
            assert config.debug is False

    def test_ensure_directories_creates_dirs(self, tmp_path):
        output_dir = tmp_path / "output"
        temp_dir = tmp_path / "temp"

        config = Config(
            output_dir=str(output_dir),
            temp_dir=str(temp_dir)
        )

        config.ensure_directories()

        assert output_dir.exists()
        assert output_dir.is_dir()
        assert temp_dir.exists()
        assert temp_dir.is_dir()

    def test_ensure_directories_existing_dirs(self, tmp_path):
        output_dir = tmp_path / "output"
        temp_dir = tmp_path / "temp"
        output_dir.mkdir()
        temp_dir.mkdir()

        config = Config(
            output_dir=str(output_dir),
            temp_dir=str(temp_dir)
        )

        config.ensure_directories()

        assert output_dir.exists()
        assert temp_dir.exists()

    def test_ensure_directories_creates_parent_dirs(self, tmp_path):
        output_dir = tmp_path / "parent" / "child" / "output"
        temp_dir = tmp_path / "parent" / "child" / "temp"

        config = Config(
            output_dir=str(output_dir),
            temp_dir=str(temp_dir)
        )

        config.ensure_directories()

        assert output_dir.exists()
        assert temp_dir.exists()

    def test_to_dict_contains_all_fields(self):
        config = Config()
        config_dict = config.to_dict()

        expected_keys = [
            "ovi_path", "output_dir", "temp_dir",
            "video_width", "video_height", "video_fps",
            "segment_duration", "model_name", "sample_steps",
            "video_guidance_scale", "audio_guidance_scale",
            "cpu_offload", "fp8", "whisper_model",
            "extract_lyrics", "crossfade_duration",
            "api_host", "api_port", "debug"
        ]

        for key in expected_keys:
            assert key in config_dict

    def test_to_dict_values_match(self):
        config = Config(
            ovi_path="/test/ovi",
            video_width=1280,
            sample_steps=75,
            debug=True
        )

        config_dict = config.to_dict()

        assert config_dict["ovi_path"] == "/test/ovi"
        assert config_dict["video_width"] == 1280
        assert config_dict["sample_steps"] == 75
        assert config_dict["debug"] is True

    def test_to_dict_returns_dict(self):
        config = Config()
        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)

    def test_video_dimensions(self):
        config = Config(video_width=1920, video_height=1080)

        assert config.video_width == 1920
        assert config.video_height == 1080

    def test_guidance_scales(self):
        config = Config(
            video_guidance_scale=5.0,
            audio_guidance_scale=2.5
        )

        assert config.video_guidance_scale == 5.0
        assert config.audio_guidance_scale == 2.5

    def test_codec_settings(self):
        config = Config(
            output_video_codec="h264",
            output_audio_codec="mp3",
            output_video_bitrate="10M",
            output_audio_bitrate="256k"
        )

        assert config.output_video_codec == "h264"
        assert config.output_audio_codec == "mp3"
        assert config.output_video_bitrate == "10M"
        assert config.output_audio_bitrate == "256k"

    def test_whisper_model_options(self):
        models = ["tiny", "base", "small", "medium", "large"]

        for model in models:
            config = Config(whisper_model=model)
            assert config.whisper_model == model

    def test_api_configuration(self):
        config = Config(
            api_host="0.0.0.0",
            api_port=8080
        )

        assert config.api_host == "0.0.0.0"
        assert config.api_port == 8080

    def test_from_env_integer_conversion(self):
        with patch.dict(os.environ, {"VIDEO_WIDTH": "1280", "SAMPLE_STEPS": "100"}, clear=True):
            config = Config.from_env()

            assert isinstance(config.video_width, int)
            assert isinstance(config.sample_steps, int)
            assert config.video_width == 1280
            assert config.sample_steps == 100

    def test_from_env_float_conversion(self):
        with patch.dict(os.environ, {"SEGMENT_DURATION": "7.5"}, clear=True):
            config = Config.from_env()

            assert isinstance(config.segment_duration, float)
            assert config.segment_duration == 7.5

    def test_crossfade_duration(self):
        config = Config(crossfade_duration=1.0)
        assert config.crossfade_duration == 1.0

    def test_fps_setting(self):
        config = Config(video_fps=30)
        assert config.video_fps == 30
