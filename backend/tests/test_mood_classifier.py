import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from src.audio_analysis.mood_classifier import MoodClassifier


class TestMoodClassifier:
    def test_initialization(self):
        classifier = MoodClassifier()
        assert hasattr(classifier, 'feature_weights')
        assert classifier.feature_weights['tempo'] == 0.2
        assert classifier.feature_weights['energy'] == 0.25

    def test_mood_categories_exist(self):
        assert len(MoodClassifier.MOOD_CATEGORIES) == 10
        assert "energetic" in MoodClassifier.MOOD_CATEGORIES
        assert "calm" in MoodClassifier.MOOD_CATEGORIES
        assert "happy" in MoodClassifier.MOOD_CATEGORIES

    @patch('librosa.beat.beat_track')
    @patch('librosa.feature.rms')
    @patch('librosa.feature.spectral_centroid')
    @patch('librosa.feature.spectral_contrast')
    @patch('librosa.feature.chroma_cqt')
    def test_extract_features(self, mock_chroma, mock_contrast, mock_centroid, mock_rms, mock_beat, sample_audio_data):
        y, sr = sample_audio_data

        mock_beat.return_value = (120.0, np.array([10, 20, 30]))
        mock_rms.return_value = np.array([[0.5, 0.6, 0.7]])
        mock_centroid.return_value = np.array([[2000.0, 2100.0, 2200.0]])
        mock_contrast.return_value = np.random.rand(7, 100)
        mock_chroma.return_value = np.random.rand(12, 100)

        classifier = MoodClassifier()
        features = classifier._extract_features(y, sr)

        assert 'tempo' in features
        assert 'energy' in features
        assert 'spectral_centroid' in features
        assert 'spectral_contrast' in features
        assert 'mode' in features
        assert 'dynamics' in features

        assert isinstance(features['tempo'], float)
        assert isinstance(features['energy'], float)
        assert isinstance(features['spectral_centroid'], float)

    @patch('librosa.beat.beat_track')
    @patch('librosa.feature.rms')
    @patch('librosa.feature.spectral_centroid')
    @patch('librosa.feature.spectral_contrast')
    @patch('librosa.feature.chroma_cqt')
    def test_classify_returns_mood(self, mock_chroma, mock_contrast, mock_centroid, mock_rms, mock_beat, sample_audio_data):
        y, sr = sample_audio_data

        mock_beat.return_value = (120.0, np.array([10, 20, 30]))
        mock_rms.return_value = np.array([[0.5, 0.6, 0.7]])
        mock_centroid.return_value = np.array([[2000.0, 2100.0, 2200.0]])
        mock_contrast.return_value = np.random.rand(7, 100)
        mock_chroma.return_value = np.random.rand(12, 100)

        classifier = MoodClassifier()
        mood = classifier.classify(y, sr)

        assert mood in MoodClassifier.MOOD_CATEGORIES
        assert isinstance(mood, str)

    @patch('librosa.beat.beat_track')
    @patch('librosa.feature.rms')
    @patch('librosa.feature.spectral_centroid')
    @patch('librosa.feature.spectral_contrast')
    @patch('librosa.feature.chroma_cqt')
    def test_classify_detailed_returns_all_moods(self, mock_chroma, mock_contrast, mock_centroid, mock_rms, mock_beat, sample_audio_data):
        y, sr = sample_audio_data

        mock_beat.return_value = (100.0, np.array([10, 20, 30]))
        mock_rms.return_value = np.array([[0.3, 0.4, 0.5]])
        mock_centroid.return_value = np.array([[1500.0, 1600.0, 1700.0]])
        mock_contrast.return_value = np.random.rand(7, 100)
        mock_chroma.return_value = np.random.rand(12, 100)

        classifier = MoodClassifier()
        scores = classifier.classify_detailed(y, sr)

        assert len(scores) == 10
        for mood in MoodClassifier.MOOD_CATEGORIES:
            assert mood in scores
            assert 0.0 <= scores[mood] <= 1.0

    def test_calculate_mood_scores_energetic(self):
        classifier = MoodClassifier()
        features = {
            'tempo': 160.0,
            'energy': 0.8,
            'spectral_centroid': 4000.0,
            'spectral_contrast': 30.0,
            'mode': 1.0,
            'dynamics': 0.5
        }

        scores = classifier._calculate_mood_scores(features)

        assert scores['energetic'] > scores['calm']
        assert scores['energetic'] > 0.5

    def test_calculate_mood_scores_calm(self):
        classifier = MoodClassifier()
        features = {
            'tempo': 60.0,
            'energy': 0.2,
            'spectral_centroid': 1000.0,
            'spectral_contrast': 10.0,
            'mode': 0.0,
            'dynamics': 0.1
        }

        scores = classifier._calculate_mood_scores(features)

        assert scores['calm'] > scores['energetic']
        assert scores['calm'] > 0.5

    def test_calculate_mood_scores_happy(self):
        classifier = MoodClassifier()
        features = {
            'tempo': 130.0,
            'energy': 0.6,
            'spectral_centroid': 2500.0,
            'spectral_contrast': 20.0,
            'mode': 1.0,
            'dynamics': 0.4
        }

        scores = classifier._calculate_mood_scores(features)

        assert scores['happy'] > scores['sad']

    def test_calculate_mood_scores_sad(self):
        classifier = MoodClassifier()
        features = {
            'tempo': 70.0,
            'energy': 0.3,
            'spectral_centroid': 1500.0,
            'spectral_contrast': 15.0,
            'mode': 0.0,
            'dynamics': 0.2
        }

        scores = classifier._calculate_mood_scores(features)

        assert scores['sad'] > scores['happy']

    def test_calculate_mood_scores_aggressive(self):
        classifier = MoodClassifier()
        features = {
            'tempo': 150.0,
            'energy': 0.9,
            'spectral_centroid': 4500.0,
            'spectral_contrast': 35.0,
            'mode': 0.5,
            'dynamics': 0.7
        }

        scores = classifier._calculate_mood_scores(features)

        assert scores['aggressive'] > 0.5

    def test_normalize_clamps_values(self):
        classifier = MoodClassifier()

        assert classifier._normalize(0.5) == 0.5
        assert classifier._normalize(-0.5) == 0.0
        assert classifier._normalize(1.5) == 1.0
        assert classifier._normalize(0.0) == 0.0
        assert classifier._normalize(1.0) == 1.0

    def test_normalize_edge_cases(self):
        classifier = MoodClassifier()

        assert classifier._normalize(float('inf')) == 1.0
        assert classifier._normalize(float('-inf')) == 0.0

    @patch('librosa.beat.beat_track')
    @patch('librosa.feature.rms')
    @patch('librosa.feature.spectral_centroid')
    @patch('librosa.feature.spectral_contrast')
    @patch('librosa.feature.chroma_cqt')
    def test_classify_with_numpy_array_tempo(self, mock_chroma, mock_contrast, mock_centroid, mock_rms, mock_beat, sample_audio_data):
        y, sr = sample_audio_data

        mock_beat.return_value = (np.array([120.0]), np.array([10, 20, 30]))
        mock_rms.return_value = np.array([[0.5, 0.6, 0.7]])
        mock_centroid.return_value = np.array([[2000.0, 2100.0, 2200.0]])
        mock_contrast.return_value = np.random.rand(7, 100)
        mock_chroma.return_value = np.random.rand(12, 100)

        classifier = MoodClassifier()
        mood = classifier.classify(y, sr)

        assert mood in MoodClassifier.MOOD_CATEGORIES

    @patch('librosa.beat.beat_track')
    @patch('librosa.feature.rms')
    @patch('librosa.feature.spectral_centroid')
    @patch('librosa.feature.spectral_contrast')
    @patch('librosa.feature.chroma_cqt')
    def test_major_vs_minor_mode_detection(self, mock_chroma, mock_contrast, mock_centroid, mock_rms, mock_beat, sample_audio_data):
        y, sr = sample_audio_data

        mock_beat.return_value = (120.0, np.array([10, 20, 30]))
        mock_rms.return_value = np.array([[0.5, 0.6, 0.7]])
        mock_centroid.return_value = np.array([[2000.0, 2100.0, 2200.0]])
        mock_contrast.return_value = np.random.rand(7, 100)

        major_chroma = np.tile(np.array([1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]).reshape(-1, 1), (1, 100))
        mock_chroma.return_value = major_chroma

        classifier = MoodClassifier()
        features = classifier._extract_features(y, sr)

        assert features['mode'] == 1.0

    @patch('librosa.beat.beat_track')
    @patch('librosa.feature.rms')
    @patch('librosa.feature.spectral_centroid')
    @patch('librosa.feature.spectral_contrast')
    @patch('librosa.feature.chroma_cqt')
    def test_all_moods_have_scores(self, mock_chroma, mock_contrast, mock_centroid, mock_rms, mock_beat, sample_audio_data):
        y, sr = sample_audio_data

        mock_beat.return_value = (120.0, np.array([10, 20, 30]))
        mock_rms.return_value = np.array([[0.5, 0.6, 0.7]])
        mock_centroid.return_value = np.array([[2000.0, 2100.0, 2200.0]])
        mock_contrast.return_value = np.random.rand(7, 100)
        mock_chroma.return_value = np.random.rand(12, 100)

        classifier = MoodClassifier()
        scores = classifier.classify_detailed(y, sr)

        expected_moods = ["energetic", "calm", "happy", "sad", "aggressive", "dreamy", "mysterious", "romantic", "epic", "playful"]
        for mood in expected_moods:
            assert mood in scores
            assert isinstance(scores[mood], float)
