import random
from typing import List, Optional
from dataclasses import dataclass

from ..audio_analysis.analyzer import AudioAnalysisResult, AudioSegment
from .visual_theme_mapper import VisualThemeMapper


@dataclass
class VideoPrompt:
    segment_index: int
    start_time: float
    end_time: float
    prompt_text: str
    audio_description: str
    negative_prompt: str


class PromptGenerator:
    def __init__(self, creativity_level: float = 0.7):
        self.theme_mapper = VisualThemeMapper()
        self.creativity_level = creativity_level

    def generate_prompts(
        self,
        analysis: AudioAnalysisResult,
        style_override: Optional[str] = None,
        custom_theme: Optional[str] = None
    ) -> List[VideoPrompt]:
        prompts = []

        for idx, segment in enumerate(analysis.segments):
            prompt = self._generate_segment_prompt(
                segment=segment,
                segment_index=idx,
                overall_mood=analysis.overall_mood,
                genre=analysis.genre_prediction,
                style_override=style_override,
                custom_theme=custom_theme
            )
            prompts.append(prompt)

        return prompts

    def _generate_segment_prompt(
        self,
        segment: AudioSegment,
        segment_index: int,
        overall_mood: str,
        genre: str,
        style_override: Optional[str] = None,
        custom_theme: Optional[str] = None
    ) -> VideoPrompt:
        visual_elements = self.theme_mapper.get_visual_elements(segment.mood)
        genre_aesthetics = self.theme_mapper.get_genre_aesthetics(genre)
        pacing = self.theme_mapper.get_tempo_pacing(segment.tempo)
        intensity = self.theme_mapper.map_energy_to_intensity(segment.energy)
        color_grading = self.theme_mapper.get_color_grading(segment.mood, genre)

        scene = random.choice(visual_elements["scenes"])
        environment = random.choice(visual_elements["environments"])
        movement = random.choice(visual_elements["movements"])
        style = style_override or random.choice(genre_aesthetics["style"])

        prompt_parts = []

        if custom_theme:
            prompt_parts.append(custom_theme)
        else:
            prompt_parts.append(scene)

        prompt_parts.append(f"set in {environment}")
        prompt_parts.append(f"with {movement} camera movement")
        prompt_parts.append(f"{style} visual style")
        prompt_parts.append(color_grading)
        prompt_parts.append(f"{intensity} visual presence")

        if segment.lyrics:
            lyrics_context = self._extract_visual_from_lyrics(segment.lyrics)
            if lyrics_context:
                prompt_parts.append(f"incorporating {lyrics_context}")

        prompt_parts.extend([
            "cinematic quality",
            "high production value",
            "professional lighting",
            f"matching {segment.mood} atmosphere"
        ])

        prompt_text = ", ".join(prompt_parts)

        audio_description = self._generate_audio_description(segment, overall_mood, genre)

        negative_prompt = self._generate_negative_prompt(segment.mood)

        return VideoPrompt(
            segment_index=segment_index,
            start_time=segment.start_time,
            end_time=segment.end_time,
            prompt_text=prompt_text,
            audio_description=audio_description,
            negative_prompt=negative_prompt
        )

    def _generate_audio_description(
        self,
        segment: AudioSegment,
        overall_mood: str,
        genre: str
    ) -> str:
        tempo_desc = "slow" if segment.tempo < 80 else "moderate" if segment.tempo < 120 else "fast" if segment.tempo < 160 else "very fast"
        energy_desc = "gentle" if segment.energy < 0.3 else "moderate" if segment.energy < 0.6 else "intense"

        return f"Audio: {energy_desc} {genre} music with {tempo_desc} tempo, {overall_mood} mood"

    def _generate_negative_prompt(self, mood: str) -> str:
        base_negatives = [
            "low quality",
            "blurry",
            "distorted",
            "amateur",
            "poorly lit",
            "overexposed",
            "underexposed",
            "artifacts",
            "noise",
            "watermark",
            "text overlay"
        ]

        mood_specific_negatives = {
            "calm": ["chaotic", "violent", "aggressive movement", "harsh lighting"],
            "energetic": ["static", "boring", "slow", "muted colors"],
            "sad": ["bright cheerful colors", "happy faces", "celebration"],
            "happy": ["dark", "gloomy", "depressing", "monochrome"],
            "aggressive": ["soft", "gentle", "pastel colors", "peaceful"],
            "dreamy": ["harsh reality", "gritty", "industrial", "sharp edges"],
            "mysterious": ["bright lighting", "clear visibility", "cheerful"],
            "romantic": ["harsh", "cold", "industrial", "violent"],
            "epic": ["small scale", "intimate", "mundane", "ordinary"],
            "playful": ["serious", "dark", "threatening", "gloomy"]
        }

        negatives = base_negatives + mood_specific_negatives.get(mood, [])
        return ", ".join(negatives)

    def _extract_visual_from_lyrics(self, lyrics: str) -> Optional[str]:
        if not lyrics:
            return None

        visual_keywords = {
            "sky": "expansive sky views",
            "sun": "warm sunlight",
            "moon": "moonlit atmosphere",
            "star": "starry night sky",
            "rain": "rainfall effects",
            "fire": "flame elements",
            "ocean": "ocean waves",
            "sea": "maritime scenery",
            "mountain": "mountain landscapes",
            "forest": "forest environment",
            "city": "urban cityscape",
            "night": "nighttime setting",
            "day": "daylight scenes",
            "love": "romantic imagery",
            "heart": "love symbolism",
            "dream": "dreamlike sequences",
            "dance": "dancing figures",
            "fly": "flying/soaring motion",
            "run": "running movement",
            "light": "dramatic lighting",
            "dark": "shadowy atmosphere",
            "gold": "golden color tones",
            "blue": "blue color palette",
            "red": "red accent colors",
            "green": "natural green elements"
        }

        lyrics_lower = lyrics.lower()
        found_visuals = []

        for keyword, visual in visual_keywords.items():
            if keyword in lyrics_lower:
                found_visuals.append(visual)

        if found_visuals:
            return ", ".join(found_visuals[:3])

        return None

    def create_ovi_prompt(self, video_prompt: VideoPrompt) -> str:
        return f"{video_prompt.prompt_text}\n\n{video_prompt.audio_description}"
