import librosa
import numpy as np
from typing import Dict, List


class MoodClassifier:
    MOOD_CATEGORIES = [
        "energetic",
        "calm",
        "happy",
        "sad",
        "aggressive",
        "dreamy",
        "mysterious",
        "romantic",
        "epic",
        "playful"
    ]

    def __init__(self):
        self.feature_weights = {
            "tempo": 0.2,
            "energy": 0.25,
            "spectral_centroid": 0.15,
            "spectral_contrast": 0.15,
            "mode": 0.15,
            "dynamics": 0.1
        }

    def classify(self, y: np.ndarray, sr: int) -> str:
        features = self._extract_features(y, sr)
        mood_scores = self._calculate_mood_scores(features)
        return max(mood_scores, key=mood_scores.get)

    def classify_detailed(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        features = self._extract_features(y, sr)
        return self._calculate_mood_scores(features)

    def _extract_features(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        tempo_val = float(tempo) if isinstance(tempo, np.ndarray) else tempo

        rms = librosa.feature.rms(y=y)[0]
        energy = float(np.mean(rms))
        dynamics = float(np.std(rms))

        spectral_centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))

        spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        contrast_mean = float(np.mean(spectral_contrast))

        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        major_profile = np.array([1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1])
        minor_profile = np.array([1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0])

        chroma_mean = np.mean(chroma, axis=1)
        major_corr = float(np.corrcoef(chroma_mean, major_profile)[0, 1])
        minor_corr = float(np.corrcoef(chroma_mean, minor_profile)[0, 1])
        mode = 1.0 if major_corr > minor_corr else 0.0

        return {
            "tempo": tempo_val,
            "energy": energy,
            "spectral_centroid": spectral_centroid,
            "spectral_contrast": contrast_mean,
            "mode": mode,
            "dynamics": dynamics
        }

    def _calculate_mood_scores(self, features: Dict[str, float]) -> Dict[str, float]:
        scores = {}

        tempo = features["tempo"]
        energy = features["energy"]
        centroid = features["spectral_centroid"]
        mode = features["mode"]
        dynamics = features["dynamics"]

        scores["energetic"] = self._normalize(
            tempo / 180 * 0.4 + energy * 0.4 + centroid / 5000 * 0.2
        )

        scores["calm"] = self._normalize(
            (1 - tempo / 180) * 0.4 + (1 - energy) * 0.4 + (1 - dynamics) * 0.2
        )

        scores["happy"] = self._normalize(
            mode * 0.4 + tempo / 150 * 0.3 + energy * 0.3
        )

        scores["sad"] = self._normalize(
            (1 - mode) * 0.4 + (1 - tempo / 150) * 0.3 + (1 - energy) * 0.3
        )

        scores["aggressive"] = self._normalize(
            energy * 0.4 + centroid / 5000 * 0.3 + dynamics * 0.3
        )

        scores["dreamy"] = self._normalize(
            (1 - energy) * 0.3 + (1 - centroid / 5000) * 0.3 + (1 - dynamics) * 0.4
        )

        scores["mysterious"] = self._normalize(
            (1 - mode) * 0.3 + dynamics * 0.4 + (1 - tempo / 150) * 0.3
        )

        scores["romantic"] = self._normalize(
            (1 - tempo / 150) * 0.3 + mode * 0.3 + (1 - dynamics) * 0.4
        )

        scores["epic"] = self._normalize(
            dynamics * 0.4 + energy * 0.3 + centroid / 5000 * 0.3
        )

        scores["playful"] = self._normalize(
            tempo / 150 * 0.4 + mode * 0.3 + dynamics * 0.3
        )

        return scores

    def _normalize(self, value: float) -> float:
        return max(0.0, min(1.0, value))
