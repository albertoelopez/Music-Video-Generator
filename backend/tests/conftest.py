import pytest
import numpy as np
from pathlib import Path
from unittest.mock import Mock, MagicMock


@pytest.fixture
def sample_audio_data():
    sr = 22050
    duration = 10.0
    num_samples = int(sr * duration)
    t = np.linspace(0, duration, num_samples)
    frequency = 440.0
    y = 0.5 * np.sin(2 * np.pi * frequency * t)
    return y, sr


@pytest.fixture
def short_audio_data():
    sr = 22050
    duration = 2.0
    num_samples = int(sr * duration)
    t = np.linspace(0, duration, num_samples)
    frequency = 440.0
    y = 0.5 * np.sin(2 * np.pi * frequency * t)
    return y, sr


@pytest.fixture
def silence_audio_data():
    sr = 22050
    duration = 5.0
    num_samples = int(sr * duration)
    y = np.zeros(num_samples)
    return y, sr


@pytest.fixture
def high_energy_audio():
    sr = 22050
    duration = 5.0
    num_samples = int(sr * duration)
    t = np.linspace(0, duration, num_samples)
    frequency = 2000.0
    y = 0.9 * np.sin(2 * np.pi * frequency * t)
    return y, sr


@pytest.fixture
def low_energy_audio():
    sr = 22050
    duration = 5.0
    num_samples = int(sr * duration)
    t = np.linspace(0, duration, num_samples)
    frequency = 200.0
    y = 0.1 * np.sin(2 * np.pi * frequency * t)
    return y, sr


@pytest.fixture
def temp_audio_file(tmp_path, sample_audio_data):
    y, sr = sample_audio_data
    audio_file = tmp_path / "test_audio.wav"

    import librosa
    import soundfile as sf
    sf.write(str(audio_file), y, sr)

    return str(audio_file)


@pytest.fixture
def temp_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def mock_librosa_load(sample_audio_data):
    def _load(path, sr=22050):
        return sample_audio_data
    return _load


@pytest.fixture
def mock_whisper_model():
    model = Mock()
    model.transcribe.return_value = {
        "text": "This is a test lyric",
        "segments": [
            {"start": 0.0, "end": 2.0, "text": "This is"},
            {"start": 2.0, "end": 4.0, "text": "a test lyric"}
        ]
    }
    return model


@pytest.fixture
def sample_beat_times():
    return np.array([0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0])


@pytest.fixture
def mock_config():
    from src.utils.config import Config
    config = Config()
    config.segment_duration = 5.0
    config.video_width = 960
    config.video_height = 960
    config.model_name = "960x960_10s"
    config.output_dir = "./test_output"
    config.temp_dir = "./test_temp"
    return config
