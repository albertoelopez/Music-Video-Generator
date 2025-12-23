import librosa
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class BeatInfo:
    times: np.ndarray
    tempo: float
    beat_strength: np.ndarray
    downbeats: np.ndarray


class BeatDetector:
    def __init__(self, sample_rate: int = 22050):
        self.sample_rate = sample_rate

    def detect(self, y: np.ndarray) -> BeatInfo:
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=self.sample_rate)
        beat_times = librosa.frames_to_time(beat_frames, sr=self.sample_rate)

        onset_env = librosa.onset.onset_strength(y=y, sr=self.sample_rate)
        beat_strength = onset_env[beat_frames] if len(beat_frames) > 0 else np.array([])

        downbeats = self._detect_downbeats(beat_times, tempo)

        return BeatInfo(
            times=beat_times,
            tempo=float(tempo) if isinstance(tempo, np.ndarray) else tempo,
            beat_strength=beat_strength,
            downbeats=downbeats
        )

    def _detect_downbeats(self, beat_times: np.ndarray, tempo: float) -> np.ndarray:
        if len(beat_times) < 4:
            return beat_times

        beats_per_bar = 4
        downbeat_indices = np.arange(0, len(beat_times), beats_per_bar)
        return beat_times[downbeat_indices]

    def get_beat_intervals(self, beat_times: np.ndarray) -> np.ndarray:
        if len(beat_times) < 2:
            return np.array([])
        return np.diff(beat_times)

    def find_tempo_changes(self, y: np.ndarray, hop_length: int = 512) -> List[Tuple[float, float]]:
        onset_env = librosa.onset.onset_strength(y=y, sr=self.sample_rate, hop_length=hop_length)

        window_size = int(10 * self.sample_rate / hop_length)
        tempo_changes = []

        for i in range(0, len(onset_env) - window_size, window_size // 2):
            window = onset_env[i:i + window_size]
            tempo = librosa.feature.tempo(onset_envelope=window, sr=self.sample_rate)[0]
            time = librosa.frames_to_time(i, sr=self.sample_rate, hop_length=hop_length)
            tempo_changes.append((time, tempo))

        return tempo_changes
