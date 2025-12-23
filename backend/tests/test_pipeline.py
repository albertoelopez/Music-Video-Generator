import pytest
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call

from src.pipeline import (
    MusicVideoPipeline,
    PipelineStatus,
    PipelineProgress,
    MusicVideoResult
)
from src.audio_analysis.analyzer import AudioAnalysisResult, AudioSegment
from src.prompt_generation.prompt_generator import VideoPrompt


class TestPipelineStatus:
    def test_pipeline_status_enum(self):
        assert PipelineStatus.IDLE.value == "idle"
        assert PipelineStatus.ANALYZING.value == "analyzing"
        assert PipelineStatus.GENERATING_PROMPTS.value == "generating_prompts"
        assert PipelineStatus.GENERATING_VIDEO.value == "generating_video"
        assert PipelineStatus.COMPOSING.value == "composing"
        assert PipelineStatus.COMPLETED.value == "completed"
        assert PipelineStatus.ERROR.value == "error"


class TestMusicVideoPipeline:
    def test_initialization_default(self):
        with patch('src.pipeline.AudioAnalyzer'):
            with patch('src.pipeline.PromptGenerator'):
                with patch('src.pipeline.MockOviVideoGenerator'):
                    with patch('src.pipeline.VideoComposer'):
                        pipeline = MusicVideoPipeline(use_mock_generator=True)

                        assert pipeline.config is not None
                        assert pipeline.progress_callback is None
                        assert pipeline.use_mock_generator is True
                        assert pipeline._current_status == PipelineStatus.IDLE

    def test_initialization_with_config(self, mock_config):
        with patch('src.pipeline.AudioAnalyzer'):
            with patch('src.pipeline.PromptGenerator'):
                with patch('src.pipeline.MockOviVideoGenerator'):
                    with patch('src.pipeline.VideoComposer'):
                        pipeline = MusicVideoPipeline(config=mock_config, use_mock_generator=True)

                        assert pipeline.config == mock_config

    def test_initialization_with_callback(self):
        callback = Mock()

        with patch('src.pipeline.AudioAnalyzer'):
            with patch('src.pipeline.PromptGenerator'):
                with patch('src.pipeline.MockOviVideoGenerator'):
                    with patch('src.pipeline.VideoComposer'):
                        pipeline = MusicVideoPipeline(progress_callback=callback, use_mock_generator=True)

                        assert pipeline.progress_callback == callback

    def test_initialization_creates_components(self):
        with patch('src.pipeline.AudioAnalyzer') as mock_analyzer:
            with patch('src.pipeline.PromptGenerator') as mock_prompt_gen:
                with patch('src.pipeline.MockOviVideoGenerator') as mock_video_gen:
                    with patch('src.pipeline.VideoComposer') as mock_composer:
                        pipeline = MusicVideoPipeline(use_mock_generator=True)

                        mock_analyzer.assert_called_once()
                        mock_prompt_gen.assert_called_once()
                        mock_video_gen.assert_called_once()
                        mock_composer.assert_called_once()

    def test_update_progress_calls_callback(self):
        callback = Mock()

        with patch('src.pipeline.AudioAnalyzer'):
            with patch('src.pipeline.PromptGenerator'):
                with patch('src.pipeline.MockOviVideoGenerator'):
                    with patch('src.pipeline.VideoComposer'):
                        pipeline = MusicVideoPipeline(progress_callback=callback, use_mock_generator=True)

                        pipeline._update_progress(
                            PipelineStatus.ANALYZING,
                            0.5,
                            "Test message",
                            1,
                            4
                        )

                        callback.assert_called_once()
                        args = callback.call_args[0][0]
                        assert isinstance(args, PipelineProgress)
                        assert args.status == PipelineStatus.ANALYZING
                        assert args.progress == 0.5
                        assert args.message == "Test message"

    def test_update_progress_updates_status(self):
        with patch('src.pipeline.AudioAnalyzer'):
            with patch('src.pipeline.PromptGenerator'):
                with patch('src.pipeline.MockOviVideoGenerator'):
                    with patch('src.pipeline.VideoComposer'):
                        pipeline = MusicVideoPipeline(use_mock_generator=True)

                        pipeline._update_progress(
                            PipelineStatus.GENERATING_VIDEO,
                            0.7,
                            "Generating",
                            3,
                            4
                        )

                        assert pipeline._current_status == PipelineStatus.GENERATING_VIDEO

    @patch('src.pipeline.validate_audio_file')
    @patch('src.pipeline.ensure_directory')
    def test_generate_invalid_audio_raises_error(self, mock_ensure_dir, mock_validate):
        mock_validate.return_value = (False, "Invalid file")

        with patch('src.pipeline.AudioAnalyzer'):
            with patch('src.pipeline.PromptGenerator'):
                with patch('src.pipeline.MockOviVideoGenerator'):
                    with patch('src.pipeline.VideoComposer'):
                        pipeline = MusicVideoPipeline(use_mock_generator=True)

                        with pytest.raises(ValueError, match="Invalid audio file"):
                            pipeline.generate("/invalid/audio.mp3")

    @patch('src.pipeline.validate_audio_file')
    @patch('src.pipeline.ensure_directory')
    @patch('shutil.rmtree')
    def test_generate_success(self, mock_rmtree, mock_ensure_dir, mock_validate, tmp_path):
        mock_validate.return_value = (True, None)
        mock_ensure_dir.return_value = str(tmp_path)

        segment = AudioSegment(0.0, 5.0, 120.0, 0.6, "happy", 2000.0)
        analysis_result = AudioAnalysisResult(
            duration=10.0,
            overall_tempo=120.0,
            overall_mood="happy",
            genre_prediction="pop",
            segments=[segment],
            beat_times=np.array([0.5, 1.0]),
            energy_profile=np.array([0.6]),
            spectral_centroid=np.array([2000.0]),
            lyrics=None
        )

        prompt = VideoPrompt(0, 0.0, 5.0, "test prompt", "audio desc", "negative")
        video_clip = {"path": "/tmp/clip_0.mp4", "start_time": 0.0, "end_time": 5.0}

        with patch('src.pipeline.AudioAnalyzer') as mock_analyzer_cls:
            mock_analyzer = Mock()
            mock_analyzer.analyze.return_value = analysis_result
            mock_analyzer_cls.return_value = mock_analyzer

            with patch('src.pipeline.PromptGenerator') as mock_prompt_cls:
                mock_prompt_gen = Mock()
                mock_prompt_gen.generate_prompts.return_value = [prompt]
                mock_prompt_cls.return_value = mock_prompt_gen

                with patch('src.pipeline.MockOviVideoGenerator') as mock_video_cls:
                    mock_video_gen = Mock()
                    mock_video_gen.generate_clips.return_value = [video_clip]
                    mock_video_cls.return_value = mock_video_gen

                    with patch('src.pipeline.VideoComposer') as mock_composer_cls:
                        mock_composer = Mock()
                        mock_composer_cls.return_value = mock_composer

                        pipeline = MusicVideoPipeline(use_mock_generator=True)

                        result = pipeline.generate("/test/audio.mp3")

                        assert isinstance(result, MusicVideoResult)
                        assert result.duration == 10.0
                        assert result.segments_generated == 1
                        assert result.analysis_summary["mood"] == "happy"
                        assert result.analysis_summary["genre"] == "pop"

    @patch('src.pipeline.validate_audio_file')
    @patch('src.pipeline.ensure_directory')
    @patch('shutil.rmtree')
    def test_generate_with_custom_output_filename(self, mock_rmtree, mock_ensure_dir, mock_validate, tmp_path):
        mock_validate.return_value = (True, None)
        mock_ensure_dir.return_value = str(tmp_path)

        segment = AudioSegment(0.0, 5.0, 120.0, 0.6, "calm", 1500.0)
        analysis_result = AudioAnalysisResult(
            duration=5.0,
            overall_tempo=100.0,
            overall_mood="calm",
            genre_prediction="ambient",
            segments=[segment],
            beat_times=np.array([0.5]),
            energy_profile=np.array([0.4]),
            spectral_centroid=np.array([1500.0]),
            lyrics=None
        )

        prompt = VideoPrompt(0, 0.0, 5.0, "calm prompt", "audio desc", "negative")
        video_clip = {"path": "/tmp/clip_0.mp4", "start_time": 0.0, "end_time": 5.0}

        with patch('src.pipeline.AudioAnalyzer') as mock_analyzer_cls:
            mock_analyzer = Mock()
            mock_analyzer.analyze.return_value = analysis_result
            mock_analyzer_cls.return_value = mock_analyzer

            with patch('src.pipeline.PromptGenerator') as mock_prompt_cls:
                mock_prompt_gen = Mock()
                mock_prompt_gen.generate_prompts.return_value = [prompt]
                mock_prompt_cls.return_value = mock_prompt_gen

                with patch('src.pipeline.MockOviVideoGenerator') as mock_video_cls:
                    mock_video_gen = Mock()
                    mock_video_gen.generate_clips.return_value = [video_clip]
                    mock_video_cls.return_value = mock_video_gen

                    with patch('src.pipeline.VideoComposer') as mock_composer_cls:
                        mock_composer = Mock()
                        mock_composer_cls.return_value = mock_composer

                        pipeline = MusicVideoPipeline(use_mock_generator=True)

                        result = pipeline.generate("/test/audio.mp3", output_filename="custom_output.mp4")

                        assert "custom_output.mp4" in result.output_path

    @patch('src.pipeline.validate_audio_file')
    @patch('src.pipeline.ensure_directory')
    @patch('shutil.rmtree')
    def test_generate_with_style_override(self, mock_rmtree, mock_ensure_dir, mock_validate, tmp_path):
        mock_validate.return_value = (True, None)
        mock_ensure_dir.return_value = str(tmp_path)

        segment = AudioSegment(0.0, 5.0, 120.0, 0.6, "energetic", 2500.0)
        analysis_result = AudioAnalysisResult(
            duration=5.0,
            overall_tempo=130.0,
            overall_mood="energetic",
            genre_prediction="electronic",
            segments=[segment],
            beat_times=np.array([0.5]),
            energy_profile=np.array([0.7]),
            spectral_centroid=np.array([2500.0]),
            lyrics=None
        )

        prompt = VideoPrompt(0, 0.0, 5.0, "cyberpunk prompt", "audio desc", "negative")
        video_clip = {"path": "/tmp/clip_0.mp4", "start_time": 0.0, "end_time": 5.0}

        with patch('src.pipeline.AudioAnalyzer') as mock_analyzer_cls:
            mock_analyzer = Mock()
            mock_analyzer.analyze.return_value = analysis_result
            mock_analyzer_cls.return_value = mock_analyzer

            with patch('src.pipeline.PromptGenerator') as mock_prompt_cls:
                mock_prompt_gen = Mock()
                mock_prompt_gen.generate_prompts.return_value = [prompt]
                mock_prompt_cls.return_value = mock_prompt_gen

                with patch('src.pipeline.MockOviVideoGenerator') as mock_video_cls:
                    mock_video_gen = Mock()
                    mock_video_gen.generate_clips.return_value = [video_clip]
                    mock_video_cls.return_value = mock_video_gen

                    with patch('src.pipeline.VideoComposer') as mock_composer_cls:
                        mock_composer = Mock()
                        mock_composer_cls.return_value = mock_composer

                        pipeline = MusicVideoPipeline(use_mock_generator=True)

                        result = pipeline.generate("/test/audio.mp3", style_override="cyberpunk")

                        mock_prompt_gen.generate_prompts.assert_called_once()
                        call_args = mock_prompt_gen.generate_prompts.call_args
                        assert call_args[1]['style_override'] == "cyberpunk"

    @patch('src.pipeline.validate_audio_file')
    @patch('src.pipeline.ensure_directory')
    @patch('shutil.rmtree')
    def test_generate_cleans_up_temp_files(self, mock_rmtree, mock_ensure_dir, mock_validate, tmp_path):
        mock_validate.return_value = (True, None)
        temp_job_dir = str(tmp_path / "job_temp")
        mock_ensure_dir.return_value = temp_job_dir

        segment = AudioSegment(0.0, 5.0, 120.0, 0.6, "happy", 2000.0)
        analysis_result = AudioAnalysisResult(
            duration=5.0,
            overall_tempo=120.0,
            overall_mood="happy",
            genre_prediction="pop",
            segments=[segment],
            beat_times=np.array([0.5]),
            energy_profile=np.array([0.6]),
            spectral_centroid=np.array([2000.0]),
            lyrics=None
        )

        prompt = VideoPrompt(0, 0.0, 5.0, "test", "desc", "neg")
        video_clip = {"path": "/tmp/clip_0.mp4", "start_time": 0.0, "end_time": 5.0}

        with patch('src.pipeline.AudioAnalyzer') as mock_analyzer_cls:
            mock_analyzer = Mock()
            mock_analyzer.analyze.return_value = analysis_result
            mock_analyzer_cls.return_value = mock_analyzer

            with patch('src.pipeline.PromptGenerator') as mock_prompt_cls:
                mock_prompt_gen = Mock()
                mock_prompt_gen.generate_prompts.return_value = [prompt]
                mock_prompt_cls.return_value = mock_prompt_gen

                with patch('src.pipeline.MockOviVideoGenerator') as mock_video_cls:
                    mock_video_gen = Mock()
                    mock_video_gen.generate_clips.return_value = [video_clip]
                    mock_video_cls.return_value = mock_video_gen

                    with patch('src.pipeline.VideoComposer') as mock_composer_cls:
                        mock_composer = Mock()
                        mock_composer_cls.return_value = mock_composer

                        with patch('os.path.exists', return_value=True):
                            pipeline = MusicVideoPipeline(use_mock_generator=True)
                            pipeline.generate("/test/audio.mp3")

                            mock_rmtree.assert_called()

    @patch('src.pipeline.validate_audio_file')
    def test_analyze_only(self, mock_validate):
        mock_validate.return_value = (True, None)

        segment = AudioSegment(0.0, 5.0, 120.0, 0.6, "happy", 2000.0, lyrics="test lyrics")
        analysis_result = AudioAnalysisResult(
            duration=10.0,
            overall_tempo=120.0,
            overall_mood="happy",
            genre_prediction="pop",
            segments=[segment],
            beat_times=np.array([0.5, 1.0, 1.5]),
            energy_profile=np.array([0.6]),
            spectral_centroid=np.array([2000.0]),
            lyrics="full lyrics"
        )

        with patch('src.pipeline.AudioAnalyzer') as mock_analyzer_cls:
            mock_analyzer = Mock()
            mock_analyzer.analyze.return_value = analysis_result
            mock_analyzer_cls.return_value = mock_analyzer

            with patch('src.pipeline.PromptGenerator'):
                with patch('src.pipeline.MockOviVideoGenerator'):
                    with patch('src.pipeline.VideoComposer'):
                        pipeline = MusicVideoPipeline(use_mock_generator=True)

                        result = pipeline.analyze_only("/test/audio.mp3")

                        assert result["duration"] == 10.0
                        assert result["tempo"] == 120.0
                        assert result["mood"] == "happy"
                        assert result["genre"] == "pop"
                        assert len(result["segments"]) == 1
                        assert result["lyrics"] == "full lyrics"
                        assert result["beat_count"] == 3

    @patch('src.pipeline.validate_audio_file')
    def test_preview_prompts(self, mock_validate):
        mock_validate.return_value = (True, None)

        segment = AudioSegment(0.0, 5.0, 120.0, 0.6, "happy", 2000.0)
        analysis_result = AudioAnalysisResult(
            duration=5.0,
            overall_tempo=120.0,
            overall_mood="happy",
            genre_prediction="pop",
            segments=[segment],
            beat_times=np.array([0.5]),
            energy_profile=np.array([0.6]),
            spectral_centroid=np.array([2000.0]),
            lyrics=None
        )

        prompt = VideoPrompt(0, 0.0, 5.0, "happy scene", "energetic music", "low quality")

        with patch('src.pipeline.AudioAnalyzer') as mock_analyzer_cls:
            mock_analyzer = Mock()
            mock_analyzer.analyze.return_value = analysis_result
            mock_analyzer_cls.return_value = mock_analyzer

            with patch('src.pipeline.PromptGenerator') as mock_prompt_cls:
                mock_prompt_gen = Mock()
                mock_prompt_gen.generate_prompts.return_value = [prompt]
                mock_prompt_cls.return_value = mock_prompt_gen

                with patch('src.pipeline.MockOviVideoGenerator'):
                    with patch('src.pipeline.VideoComposer'):
                        pipeline = MusicVideoPipeline(use_mock_generator=True)

                        result = pipeline.preview_prompts("/test/audio.mp3")

                        assert len(result) == 1
                        assert result[0]["segment_index"] == 0
                        assert result[0]["prompt_text"] == "happy scene"
                        assert result[0]["audio_description"] == "energetic music"

    def test_status_property(self):
        with patch('src.pipeline.AudioAnalyzer'):
            with patch('src.pipeline.PromptGenerator'):
                with patch('src.pipeline.MockOviVideoGenerator'):
                    with patch('src.pipeline.VideoComposer'):
                        pipeline = MusicVideoPipeline(use_mock_generator=True)

                        assert pipeline.status == PipelineStatus.IDLE

                        pipeline._update_progress(PipelineStatus.ANALYZING, 0.1, "Analyzing", 1, 4)

                        assert pipeline.status == PipelineStatus.ANALYZING

    @patch('src.pipeline.validate_audio_file')
    @patch('src.pipeline.ensure_directory')
    @patch('shutil.rmtree')
    def test_generate_handles_exception(self, mock_rmtree, mock_ensure_dir, mock_validate):
        mock_validate.return_value = (True, None)
        mock_ensure_dir.return_value = "/tmp/job"

        with patch('src.pipeline.AudioAnalyzer') as mock_analyzer_cls:
            mock_analyzer = Mock()
            mock_analyzer.analyze.side_effect = Exception("Analysis failed")
            mock_analyzer_cls.return_value = mock_analyzer

            with patch('src.pipeline.PromptGenerator'):
                with patch('src.pipeline.MockOviVideoGenerator'):
                    with patch('src.pipeline.VideoComposer'):
                        with patch('os.path.exists', return_value=True):
                            pipeline = MusicVideoPipeline(use_mock_generator=True)

                            with pytest.raises(Exception, match="Analysis failed"):
                                pipeline.generate("/test/audio.mp3")

                            assert pipeline.status == PipelineStatus.ERROR
                            mock_rmtree.assert_called()

    @patch('src.pipeline.OviVideoGenerator')
    def test_initialization_with_real_generator(self, mock_ovi_gen):
        with patch('src.pipeline.AudioAnalyzer'):
            with patch('src.pipeline.PromptGenerator'):
                with patch('src.pipeline.VideoComposer'):
                    pipeline = MusicVideoPipeline(use_mock_generator=False)

                    mock_ovi_gen.assert_called_once()
                    assert not pipeline.use_mock_generator
