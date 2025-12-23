import os
from typing import Optional, List, Tuple
from dataclasses import dataclass


@dataclass
class TimestampedLyric:
    start_time: float
    end_time: float
    text: str


class LyricsExtractor:
    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self._model = None

    def _load_model(self):
        if self._model is None:
            try:
                import whisper
                self._model = whisper.load_model(self.model_size)
            except ImportError:
                raise ImportError(
                    "whisper-openai is required for lyrics extraction. "
                    "Install it with: pip install whisper-openai"
                )
        return self._model

    def extract(self, audio_path: str) -> Optional[str]:
        if not os.path.exists(audio_path):
            return None

        try:
            model = self._load_model()
            result = model.transcribe(audio_path)
            return result.get("text", "").strip()
        except Exception as e:
            print(f"Error extracting lyrics: {e}")
            return None

    def extract_with_timestamps(self, audio_path: str) -> List[TimestampedLyric]:
        if not os.path.exists(audio_path):
            return []

        try:
            model = self._load_model()
            result = model.transcribe(audio_path, word_timestamps=True)

            lyrics = []
            segments = result.get("segments", [])

            for segment in segments:
                lyrics.append(TimestampedLyric(
                    start_time=segment.get("start", 0.0),
                    end_time=segment.get("end", 0.0),
                    text=segment.get("text", "").strip()
                ))

            return lyrics
        except Exception as e:
            print(f"Error extracting timestamped lyrics: {e}")
            return []

    def get_lyrics_for_segment(
        self,
        timestamped_lyrics: List[TimestampedLyric],
        start_time: float,
        end_time: float
    ) -> str:
        relevant_lyrics = []

        for lyric in timestamped_lyrics:
            if lyric.start_time >= start_time and lyric.end_time <= end_time:
                relevant_lyrics.append(lyric.text)
            elif lyric.start_time < end_time and lyric.end_time > start_time:
                relevant_lyrics.append(lyric.text)

        return " ".join(relevant_lyrics)
