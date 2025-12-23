import librosa
import numpy as np
from dataclasses import dataclass
from typing import List, Optional, Tuple
from pathlib import Path

from .beat_detector import BeatDetector
from .mood_classifier import MoodClassifier
from .lyrics_extractor import LyricsExtractor


@dataclass
class AudioSegment:
    start_time: float
    end_time: float
    tempo: float
    energy: float
    mood: str
    dominant_frequency: float
    lyrics: Optional[str] = None


@dataclass
class AudioAnalysisResult:
    duration: float
    overall_tempo: float
    overall_mood: str
    genre_prediction: str
    segments: List[AudioSegment]
    beat_times: np.ndarray
    energy_profile: np.ndarray
    spectral_centroid: np.ndarray
    lyrics: Optional[str] = None


class AudioAnalyzer:
    def __init__(self, sample_rate: int = 22050, segment_duration: float = 5.0):
        self.sample_rate = sample_rate
        self.segment_duration = segment_duration
        self.beat_detector = BeatDetector(sample_rate)
        self.mood_classifier = MoodClassifier()
        self.lyrics_extractor = LyricsExtractor()

    def load_audio(self, audio_path: str) -> Tuple[np.ndarray, int]:
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        y, sr = librosa.load(str(audio_path), sr=self.sample_rate)
        return y, sr

    def analyze(self, audio_path: str, extract_lyrics: bool = True) -> AudioAnalysisResult:
        y, sr = self.load_audio(audio_path)
        duration = librosa.get_duration(y=y, sr=sr)

        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)

        rms = librosa.feature.rms(y=y)[0]
        energy_profile = rms / np.max(rms) if np.max(rms) > 0 else rms

        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]

        overall_mood = self.mood_classifier.classify(y, sr)
        genre_prediction = self._predict_genre(y, sr)

        lyrics = None
        if extract_lyrics:
            lyrics = self.lyrics_extractor.extract(audio_path)

        segments = self._create_segments(y, sr, duration, beat_times, lyrics)

        return AudioAnalysisResult(
            duration=duration,
            overall_tempo=float(tempo) if isinstance(tempo, np.ndarray) else tempo,
            overall_mood=overall_mood,
            genre_prediction=genre_prediction,
            segments=segments,
            beat_times=beat_times,
            energy_profile=energy_profile,
            spectral_centroid=spectral_centroid,
            lyrics=lyrics
        )

    def _create_segments(
        self,
        y: np.ndarray,
        sr: int,
        duration: float,
        beat_times: np.ndarray,
        lyrics: Optional[str]
    ) -> List[AudioSegment]:
        segments = []
        num_segments = int(np.ceil(duration / self.segment_duration))

        for i in range(num_segments):
            start_time = i * self.segment_duration
            end_time = min((i + 1) * self.segment_duration, duration)

            start_sample = int(start_time * sr)
            end_sample = int(end_time * sr)
            segment_audio = y[start_sample:end_sample]

            if len(segment_audio) < sr * 0.5:
                continue

            segment_tempo, _ = librosa.beat.beat_track(y=segment_audio, sr=sr)

            rms = librosa.feature.rms(y=segment_audio)[0]
            energy = float(np.mean(rms))

            mood = self.mood_classifier.classify(segment_audio, sr)

            spectral_centroid = librosa.feature.spectral_centroid(y=segment_audio, sr=sr)[0]
            dominant_freq = float(np.mean(spectral_centroid))

            segment_lyrics = None
            if lyrics:
                segment_lyrics = self._extract_segment_lyrics(lyrics, start_time, end_time)

            segments.append(AudioSegment(
                start_time=start_time,
                end_time=end_time,
                tempo=float(segment_tempo) if isinstance(segment_tempo, np.ndarray) else segment_tempo,
                energy=energy,
                mood=mood,
                dominant_frequency=dominant_freq,
                lyrics=segment_lyrics
            ))

        return segments

    def _predict_genre(self, y: np.ndarray, sr: int) -> str:
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        tempo_val = float(tempo) if isinstance(tempo, np.ndarray) else tempo

        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
        spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
        zero_crossing = np.mean(librosa.feature.zero_crossing_rate(y))

        if tempo_val > 140 and spectral_centroid > 3000:
            return "electronic"
        elif tempo_val > 120 and zero_crossing > 0.1:
            return "rock"
        elif tempo_val < 80 and spectral_centroid < 2000:
            return "ambient"
        elif 90 < tempo_val < 130 and spectral_centroid < 2500:
            return "hip-hop"
        elif tempo_val < 100 and spectral_rolloff < 4000:
            return "classical"
        elif 100 < tempo_val < 130:
            return "pop"
        else:
            return "general"

    def _extract_segment_lyrics(
        self,
        full_lyrics: str,
        start_time: float,
        end_time: float
    ) -> Optional[str]:
        return None
