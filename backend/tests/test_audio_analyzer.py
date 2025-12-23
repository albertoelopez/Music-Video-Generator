import pytest
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock

from src.audio_analysis.analyzer import AudioAnalyzer, AudioSegment, AudioAnalysisResult


class TestAudioAnalyzer:
    def test_initialization_default(self):
        analyzer = AudioAnalyzer()
        assert analyzer.sample_rate == 22050
        assert analyzer.segment_duration == 5.0
        assert hasattr(analyzer, 'beat_detector')
        assert hasattr(analyzer, 'mood_classifier')
        assert hasattr(analyzer, 'lyrics_extractor')

    def test_initialization_custom_params(self):
        analyzer = AudioAnalyzer(sample_rate=44100, segment_duration=10.0)
        assert analyzer.sample_rate == 44100
        assert analyzer.segment_duration == 10.0

    @patch('librosa.load')
    def test_load_audio_success(self, mock_load, temp_audio_file, sample_audio_data):
        y, sr = sample_audio_data
        mock_load.return_value = (y, sr)

        analyzer = AudioAnalyzer()
        loaded_y, loaded_sr = analyzer.load_audio(temp_audio_file)

        np.testing.assert_array_equal(loaded_y, y)
        assert loaded_sr == sr

    def test_load_audio_file_not_found(self):
        analyzer = AudioAnalyzer()

        with pytest.raises(FileNotFoundError):
            analyzer.load_audio("/nonexistent/path/to/audio.wav")

    @patch('librosa.load')
    @patch('librosa.get_duration')
    @patch('librosa.beat.beat_track')
    @patch('librosa.frames_to_time')
    @patch('librosa.feature.rms')
    @patch('librosa.feature.spectral_centroid')
    def test_analyze_basic(self, mock_centroid, mock_rms, mock_frames, mock_beat, mock_duration, mock_load, temp_audio_file, sample_audio_data):
        y, sr = sample_audio_data
        mock_load.return_value = (y, sr)
        mock_duration.return_value = 10.0
        mock_beat.return_value = (120.0, np.array([10, 20, 30, 40]))
        mock_frames.return_value = np.array([0.5, 1.0, 1.5, 2.0])
        mock_rms.return_value = np.array([[0.5, 0.6, 0.7]])
        mock_centroid.return_value = np.array([[2000.0, 2100.0, 2200.0]])

        with patch.object(AudioAnalyzer, '_create_segments', return_value=[]):
            with patch('src.audio_analysis.analyzer.MoodClassifier') as mock_mood_cls:
                mock_mood_instance = Mock()
                mock_mood_instance.classify.return_value = "happy"
                mock_mood_cls.return_value = mock_mood_instance

                with patch('src.audio_analysis.analyzer.LyricsExtractor') as mock_lyrics_cls:
                    mock_lyrics_instance = Mock()
                    mock_lyrics_instance.extract.return_value = None
                    mock_lyrics_cls.return_value = mock_lyrics_instance

                    analyzer = AudioAnalyzer()
                    result = analyzer.analyze(temp_audio_file, extract_lyrics=False)

                    assert isinstance(result, AudioAnalysisResult)
                    assert result.duration == 10.0
                    assert result.overall_tempo == 120.0
                    assert result.overall_mood == "happy"
                    assert len(result.beat_times) == 4

    @patch('librosa.load')
    @patch('librosa.get_duration')
    @patch('librosa.beat.beat_track')
    @patch('librosa.frames_to_time')
    @patch('librosa.feature.rms')
    @patch('librosa.feature.spectral_centroid')
    def test_analyze_with_lyrics(self, mock_centroid, mock_rms, mock_frames, mock_beat, mock_duration, mock_load, temp_audio_file, sample_audio_data):
        y, sr = sample_audio_data
        mock_load.return_value = (y, sr)
        mock_duration.return_value = 10.0
        mock_beat.return_value = (120.0, np.array([10, 20, 30, 40]))
        mock_frames.return_value = np.array([0.5, 1.0, 1.5, 2.0])
        mock_rms.return_value = np.array([[0.5, 0.6, 0.7]])
        mock_centroid.return_value = np.array([[2000.0, 2100.0, 2200.0]])

        with patch.object(AudioAnalyzer, '_create_segments', return_value=[]):
            with patch('src.audio_analysis.analyzer.MoodClassifier') as mock_mood_cls:
                mock_mood_instance = Mock()
                mock_mood_instance.classify.return_value = "energetic"
                mock_mood_cls.return_value = mock_mood_instance

                with patch('src.audio_analysis.analyzer.LyricsExtractor') as mock_lyrics_cls:
                    mock_lyrics_instance = Mock()
                    mock_lyrics_instance.extract.return_value = "Test lyrics here"
                    mock_lyrics_cls.return_value = mock_lyrics_instance

                    analyzer = AudioAnalyzer()
                    result = analyzer.analyze(temp_audio_file, extract_lyrics=True)

                    assert result.lyrics == "Test lyrics here"
                    mock_lyrics_instance.extract.assert_called_once_with(temp_audio_file)

    def test_predict_genre_electronic(self):
        analyzer = AudioAnalyzer()
        y = np.random.randn(22050 * 5)
        sr = 22050

        with patch('librosa.beat.beat_track', return_value=(150.0, np.array([10, 20]))):
            with patch('librosa.feature.spectral_centroid', return_value=np.array([[3500.0]])):
                with patch('librosa.feature.spectral_rolloff', return_value=np.array([[5000.0]])):
                    with patch('librosa.feature.zero_crossing_rate', return_value=np.array([[0.05]])):
                        genre = analyzer._predict_genre(y, sr)
                        assert genre == "electronic"

    def test_predict_genre_rock(self):
        analyzer = AudioAnalyzer()
        y = np.random.randn(22050 * 5)
        sr = 22050

        with patch('librosa.beat.beat_track', return_value=(130.0, np.array([10, 20]))):
            with patch('librosa.feature.spectral_centroid', return_value=np.array([[2500.0]])):
                with patch('librosa.feature.spectral_rolloff', return_value=np.array([[4500.0]])):
                    with patch('librosa.feature.zero_crossing_rate', return_value=np.array([[0.15]])):
                        genre = analyzer._predict_genre(y, sr)
                        assert genre == "rock"

    def test_predict_genre_ambient(self):
        analyzer = AudioAnalyzer()
        y = np.random.randn(22050 * 5)
        sr = 22050

        with patch('librosa.beat.beat_track', return_value=(70.0, np.array([10, 20]))):
            with patch('librosa.feature.spectral_centroid', return_value=np.array([[1500.0]])):
                with patch('librosa.feature.spectral_rolloff', return_value=np.array([[3000.0]])):
                    with patch('librosa.feature.zero_crossing_rate', return_value=np.array([[0.05]])):
                        genre = analyzer._predict_genre(y, sr)
                        assert genre == "ambient"

    def test_predict_genre_hip_hop(self):
        analyzer = AudioAnalyzer()
        y = np.random.randn(22050 * 5)
        sr = 22050

        with patch('librosa.beat.beat_track', return_value=(100.0, np.array([10, 20]))):
            with patch('librosa.feature.spectral_centroid', return_value=np.array([[2000.0]])):
                with patch('librosa.feature.spectral_rolloff', return_value=np.array([[4000.0]])):
                    with patch('librosa.feature.zero_crossing_rate', return_value=np.array([[0.05]])):
                        genre = analyzer._predict_genre(y, sr)
                        assert genre == "hip-hop"

    def test_predict_genre_pop(self):
        analyzer = AudioAnalyzer()
        y = np.random.randn(22050 * 5)
        sr = 22050

        with patch('librosa.beat.beat_track', return_value=(115.0, np.array([10, 20]))):
            with patch('librosa.feature.spectral_centroid', return_value=np.array([[2500.0]])):
                with patch('librosa.feature.spectral_rolloff', return_value=np.array([[4500.0]])):
                    with patch('librosa.feature.zero_crossing_rate', return_value=np.array([[0.05]])):
                        genre = analyzer._predict_genre(y, sr)
                        assert genre == "pop"

    @patch('librosa.beat.beat_track')
    @patch('librosa.feature.rms')
    @patch('librosa.feature.spectral_centroid')
    def test_create_segments(self, mock_centroid, mock_rms, mock_beat):
        analyzer = AudioAnalyzer(segment_duration=5.0)

        y = np.random.randn(22050 * 12)
        sr = 22050
        duration = 12.0
        beat_times = np.array([0.5, 1.0, 1.5, 2.0])

        mock_beat.return_value = (120.0, np.array([10, 20]))
        mock_rms.return_value = np.array([[0.5, 0.6]])
        mock_centroid.return_value = np.array([[2000.0, 2100.0]])

        with patch('src.audio_analysis.analyzer.MoodClassifier') as mock_mood_cls:
            mock_mood_instance = Mock()
            mock_mood_instance.classify.return_value = "happy"
            mock_mood_cls.return_value = mock_mood_instance
            analyzer.mood_classifier = mock_mood_instance

            segments = analyzer._create_segments(y, sr, duration, beat_times, None)

            assert len(segments) == 3
            assert all(isinstance(seg, AudioSegment) for seg in segments)
            assert segments[0].start_time == 0.0
            assert segments[0].end_time == 5.0
            assert segments[1].start_time == 5.0
            assert segments[1].end_time == 10.0

    @patch('librosa.beat.beat_track')
    @patch('librosa.feature.rms')
    @patch('librosa.feature.spectral_centroid')
    def test_create_segments_skips_short_segments(self, mock_centroid, mock_rms, mock_beat):
        analyzer = AudioAnalyzer(segment_duration=5.0)

        y = np.random.randn(22050 * 6)
        sr = 22050
        duration = 6.0
        beat_times = np.array([0.5, 1.0, 1.5])

        mock_beat.return_value = (120.0, np.array([10, 20]))
        mock_rms.return_value = np.array([[0.5, 0.6]])
        mock_centroid.return_value = np.array([[2000.0, 2100.0]])

        with patch('src.audio_analysis.analyzer.MoodClassifier') as mock_mood_cls:
            mock_mood_instance = Mock()
            mock_mood_instance.classify.return_value = "calm"
            mock_mood_cls.return_value = mock_mood_instance
            analyzer.mood_classifier = mock_mood_instance

            segments = analyzer._create_segments(y, sr, duration, beat_times, None)

            assert len(segments) == 2

    def test_extract_segment_lyrics_returns_none(self):
        analyzer = AudioAnalyzer()
        result = analyzer._extract_segment_lyrics("Full lyrics text", 0.0, 5.0)
        assert result is None

    @patch('librosa.beat.beat_track')
    def test_analyze_handles_numpy_array_tempo(self, mock_beat, temp_audio_file, sample_audio_data):
        y, sr = sample_audio_data

        mock_beat.return_value = (np.array([120.0]), np.array([10, 20, 30]))

        with patch('librosa.load', return_value=(y, sr)):
            with patch('librosa.get_duration', return_value=10.0):
                with patch('librosa.frames_to_time', return_value=np.array([0.5, 1.0, 1.5])):
                    with patch('librosa.feature.rms', return_value=np.array([[0.5, 0.6]])):
                        with patch('librosa.feature.spectral_centroid', return_value=np.array([[2000.0]])):
                            with patch.object(AudioAnalyzer, '_create_segments', return_value=[]):
                                with patch('src.audio_analysis.analyzer.MoodClassifier') as mock_mood_cls:
                                    mock_mood_instance = Mock()
                                    mock_mood_instance.classify.return_value = "happy"
                                    mock_mood_cls.return_value = mock_mood_instance

                                    with patch('src.audio_analysis.analyzer.LyricsExtractor') as mock_lyrics_cls:
                                        mock_lyrics_instance = Mock()
                                        mock_lyrics_instance.extract.return_value = None
                                        mock_lyrics_cls.return_value = mock_lyrics_instance

                                        analyzer = AudioAnalyzer()
                                        result = analyzer.analyze(temp_audio_file, extract_lyrics=False)

                                        assert isinstance(result.overall_tempo, float)
                                        assert result.overall_tempo == 120.0

    @patch('librosa.feature.rms')
    def test_energy_profile_normalization(self, mock_rms, sample_audio_data, temp_audio_file):
        y, sr = sample_audio_data

        mock_rms.return_value = np.array([[0.1, 0.5, 1.0, 0.3]])

        with patch('librosa.load', return_value=(y, sr)):
            with patch('librosa.get_duration', return_value=10.0):
                with patch('librosa.beat.beat_track', return_value=(120.0, np.array([10, 20]))):
                    with patch('librosa.frames_to_time', return_value=np.array([0.5, 1.0])):
                        with patch('librosa.feature.spectral_centroid', return_value=np.array([[2000.0]])):
                            with patch.object(AudioAnalyzer, '_create_segments', return_value=[]):
                                with patch('src.audio_analysis.analyzer.MoodClassifier') as mock_mood_cls:
                                    mock_mood_instance = Mock()
                                    mock_mood_instance.classify.return_value = "energetic"
                                    mock_mood_cls.return_value = mock_mood_instance

                                    with patch('src.audio_analysis.analyzer.LyricsExtractor') as mock_lyrics_cls:
                                        mock_lyrics_instance = Mock()
                                        mock_lyrics_instance.extract.return_value = None
                                        mock_lyrics_cls.return_value = mock_lyrics_instance

                                        analyzer = AudioAnalyzer()
                                        result = analyzer.analyze(temp_audio_file, extract_lyrics=False)

                                        assert np.max(result.energy_profile) <= 1.0
                                        assert np.min(result.energy_profile) >= 0.0
