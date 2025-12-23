import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from src.audio_analysis.beat_detector import BeatDetector, BeatInfo


class TestBeatDetector:
    def test_initialization(self):
        detector = BeatDetector(sample_rate=22050)
        assert detector.sample_rate == 22050

    def test_initialization_custom_sample_rate(self):
        detector = BeatDetector(sample_rate=44100)
        assert detector.sample_rate == 44100

    @patch('librosa.beat.beat_track')
    @patch('librosa.frames_to_time')
    @patch('librosa.onset.onset_strength')
    def test_detect_returns_beat_info(self, mock_onset, mock_frames, mock_beat_track, sample_audio_data):
        y, sr = sample_audio_data

        beat_frames = np.array([1, 2, 3, 4])
        mock_beat_track.return_value = (120.0, beat_frames)
        mock_frames.return_value = np.array([0.5, 1.0, 1.5, 2.0])
        onset_env = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
        mock_onset.return_value = onset_env

        detector = BeatDetector(sample_rate=sr)
        result = detector.detect(y)

        assert isinstance(result, BeatInfo)
        assert result.tempo == 120.0
        assert len(result.times) == 4
        assert len(result.beat_strength) == 4

    @patch('librosa.beat.beat_track')
    @patch('librosa.frames_to_time')
    @patch('librosa.onset.onset_strength')
    def test_detect_with_empty_beats(self, mock_onset, mock_frames, mock_beat_track, sample_audio_data):
        y, sr = sample_audio_data

        mock_beat_track.return_value = (120.0, np.array([]))
        mock_frames.return_value = np.array([])
        mock_onset.return_value = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6])

        detector = BeatDetector(sample_rate=sr)
        result = detector.detect(y)

        assert isinstance(result, BeatInfo)
        assert result.tempo == 120.0
        assert len(result.times) == 0
        assert len(result.beat_strength) == 0

    def test_detect_downbeats_with_sufficient_beats(self):
        detector = BeatDetector()
        beat_times = np.array([0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0])
        tempo = 120.0

        downbeats = detector._detect_downbeats(beat_times, tempo)

        assert len(downbeats) == 2
        assert downbeats[0] == 0.5
        assert downbeats[1] == 2.5

    def test_detect_downbeats_with_insufficient_beats(self):
        detector = BeatDetector()
        beat_times = np.array([0.5, 1.0, 1.5])
        tempo = 120.0

        downbeats = detector._detect_downbeats(beat_times, tempo)

        assert len(downbeats) == 3
        np.testing.assert_array_equal(downbeats, beat_times)

    def test_get_beat_intervals_normal(self):
        detector = BeatDetector()
        beat_times = np.array([0.5, 1.0, 1.5, 2.0])

        intervals = detector.get_beat_intervals(beat_times)

        assert len(intervals) == 3
        np.testing.assert_almost_equal(intervals, [0.5, 0.5, 0.5])

    def test_get_beat_intervals_insufficient_beats(self):
        detector = BeatDetector()
        beat_times = np.array([0.5])

        intervals = detector.get_beat_intervals(beat_times)

        assert len(intervals) == 0

    def test_get_beat_intervals_empty(self):
        detector = BeatDetector()
        beat_times = np.array([])

        intervals = detector.get_beat_intervals(beat_times)

        assert len(intervals) == 0

    @patch('librosa.onset.onset_strength')
    @patch('librosa.feature.tempo')
    @patch('librosa.frames_to_time')
    def test_find_tempo_changes(self, mock_frames_to_time, mock_tempo, mock_onset, sample_audio_data):
        y, sr = sample_audio_data

        onset_env = np.random.rand(1000)
        mock_onset.return_value = onset_env
        mock_tempo.return_value = np.array([120.0])
        mock_frames_to_time.return_value = 1.0

        detector = BeatDetector(sample_rate=sr)
        tempo_changes = detector.find_tempo_changes(y, hop_length=512)

        assert isinstance(tempo_changes, list)
        assert len(tempo_changes) > 0
        assert all(isinstance(tc, tuple) for tc in tempo_changes)
        assert all(len(tc) == 2 for tc in tempo_changes)

    @patch('librosa.onset.onset_strength')
    def test_find_tempo_changes_with_custom_hop_length(self, mock_onset, sample_audio_data):
        y, sr = sample_audio_data
        mock_onset.return_value = np.random.rand(500)

        detector = BeatDetector(sample_rate=sr)
        tempo_changes = detector.find_tempo_changes(y, hop_length=1024)

        mock_onset.assert_called_once()
        assert mock_onset.call_args[1]['hop_length'] == 1024

    @patch('librosa.beat.beat_track')
    @patch('librosa.frames_to_time')
    @patch('librosa.onset.onset_strength')
    def test_detect_with_numpy_array_tempo(self, mock_onset, mock_frames, mock_beat_track, sample_audio_data):
        y, sr = sample_audio_data

        beat_frames = np.array([1, 2, 3])
        mock_beat_track.return_value = (np.array([120.0]), beat_frames)
        mock_frames.return_value = np.array([0.5, 1.0, 1.5])
        onset_env = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        mock_onset.return_value = onset_env

        detector = BeatDetector(sample_rate=sr)
        result = detector.detect(y)

        assert isinstance(result.tempo, float)
        assert result.tempo == 120.0

    @patch('librosa.beat.beat_track')
    @patch('librosa.frames_to_time')
    @patch('librosa.onset.onset_strength')
    def test_detect_integration(self, mock_onset, mock_frames, mock_beat_track, high_energy_audio):
        y, sr = high_energy_audio

        beat_frames = np.array([5, 10, 15, 20, 25, 30])
        mock_beat_track.return_value = (140.0, beat_frames)
        mock_frames.return_value = np.array([0.25, 0.5, 0.75, 1.0, 1.25, 1.5])
        onset_values = np.random.rand(35)
        mock_onset.return_value = onset_values

        detector = BeatDetector(sample_rate=sr)
        result = detector.detect(y)

        assert result.tempo == 140.0
        assert len(result.times) == 6
        assert len(result.downbeats) == 2
        assert isinstance(result.beat_strength, np.ndarray)
