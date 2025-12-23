import pytest
from unittest.mock import Mock, patch
import random

from src.prompt_generation.prompt_generator import PromptGenerator, VideoPrompt
from src.audio_analysis.analyzer import AudioAnalysisResult, AudioSegment
import numpy as np


class TestPromptGenerator:
    def test_initialization_default(self):
        generator = PromptGenerator()
        assert generator.creativity_level == 0.7
        assert hasattr(generator, 'theme_mapper')

    def test_initialization_custom_creativity(self):
        generator = PromptGenerator(creativity_level=0.5)
        assert generator.creativity_level == 0.5

    def test_generate_prompts_basic(self):
        generator = PromptGenerator()

        segment1 = AudioSegment(
            start_time=0.0,
            end_time=5.0,
            tempo=120.0,
            energy=0.6,
            mood="happy",
            dominant_frequency=2000.0,
            lyrics=None
        )

        segment2 = AudioSegment(
            start_time=5.0,
            end_time=10.0,
            tempo=130.0,
            energy=0.7,
            mood="energetic",
            dominant_frequency=2500.0,
            lyrics=None
        )

        analysis = AudioAnalysisResult(
            duration=10.0,
            overall_tempo=125.0,
            overall_mood="happy",
            genre_prediction="pop",
            segments=[segment1, segment2],
            beat_times=np.array([0.5, 1.0, 1.5]),
            energy_profile=np.array([0.5, 0.6, 0.7]),
            spectral_centroid=np.array([2000.0, 2100.0]),
            lyrics=None
        )

        prompts = generator.generate_prompts(analysis)

        assert len(prompts) == 2
        assert all(isinstance(p, VideoPrompt) for p in prompts)
        assert prompts[0].segment_index == 0
        assert prompts[1].segment_index == 1

    def test_generate_prompts_with_style_override(self):
        generator = PromptGenerator()

        segment = AudioSegment(
            start_time=0.0,
            end_time=5.0,
            tempo=120.0,
            energy=0.5,
            mood="calm",
            dominant_frequency=1500.0,
            lyrics=None
        )

        analysis = AudioAnalysisResult(
            duration=5.0,
            overall_tempo=120.0,
            overall_mood="calm",
            genre_prediction="ambient",
            segments=[segment],
            beat_times=np.array([0.5]),
            energy_profile=np.array([0.5]),
            spectral_centroid=np.array([1500.0]),
            lyrics=None
        )

        prompts = generator.generate_prompts(analysis, style_override="cyberpunk")

        assert "cyberpunk" in prompts[0].prompt_text

    def test_generate_prompts_with_custom_theme(self):
        generator = PromptGenerator()

        segment = AudioSegment(
            start_time=0.0,
            end_time=5.0,
            tempo=100.0,
            energy=0.4,
            mood="dreamy",
            dominant_frequency=1200.0,
            lyrics=None
        )

        analysis = AudioAnalysisResult(
            duration=5.0,
            overall_tempo=100.0,
            overall_mood="dreamy",
            genre_prediction="ambient",
            segments=[segment],
            beat_times=np.array([0.5]),
            energy_profile=np.array([0.4]),
            spectral_centroid=np.array([1200.0]),
            lyrics=None
        )

        custom = "underwater fantasy world"
        prompts = generator.generate_prompts(analysis, custom_theme=custom)

        assert custom in prompts[0].prompt_text

    def test_generate_segment_prompt_structure(self):
        generator = PromptGenerator()

        segment = AudioSegment(
            start_time=0.0,
            end_time=5.0,
            tempo=120.0,
            energy=0.6,
            mood="epic",
            dominant_frequency=2000.0,
            lyrics=None
        )

        prompt = generator._generate_segment_prompt(
            segment=segment,
            segment_index=0,
            overall_mood="epic",
            genre="classical"
        )

        assert isinstance(prompt, VideoPrompt)
        assert prompt.segment_index == 0
        assert prompt.start_time == 0.0
        assert prompt.end_time == 5.0
        assert len(prompt.prompt_text) > 0
        assert len(prompt.audio_description) > 0
        assert len(prompt.negative_prompt) > 0

    def test_generate_segment_prompt_with_lyrics(self):
        generator = PromptGenerator()

        segment = AudioSegment(
            start_time=0.0,
            end_time=5.0,
            tempo=110.0,
            energy=0.5,
            mood="romantic",
            dominant_frequency=1800.0,
            lyrics="stars in the night sky"
        )

        with patch.object(generator, '_extract_visual_from_lyrics', return_value="starry night sky"):
            prompt = generator._generate_segment_prompt(
                segment=segment,
                segment_index=0,
                overall_mood="romantic",
                genre="pop"
            )

            assert "starry night sky" in prompt.prompt_text

    def test_generate_audio_description_slow_gentle(self):
        generator = PromptGenerator()

        segment = AudioSegment(
            start_time=0.0,
            end_time=5.0,
            tempo=70.0,
            energy=0.2,
            mood="calm",
            dominant_frequency=1000.0
        )

        description = generator._generate_audio_description(segment, "calm", "ambient")

        assert "slow" in description
        assert "gentle" in description
        assert "ambient" in description
        assert "calm" in description

    def test_generate_audio_description_fast_intense(self):
        generator = PromptGenerator()

        segment = AudioSegment(
            start_time=0.0,
            end_time=5.0,
            tempo=170.0,
            energy=0.8,
            mood="energetic",
            dominant_frequency=3000.0
        )

        description = generator._generate_audio_description(segment, "energetic", "electronic")

        assert "very fast" in description
        assert "intense" in description
        assert "electronic" in description

    def test_generate_audio_description_tempo_ranges(self):
        generator = PromptGenerator()

        segment_slow = AudioSegment(0.0, 5.0, 75.0, 0.5, "calm", 1500.0)
        segment_moderate = AudioSegment(0.0, 5.0, 100.0, 0.5, "happy", 2000.0)
        segment_fast = AudioSegment(0.0, 5.0, 140.0, 0.5, "energetic", 2500.0)
        segment_very_fast = AudioSegment(0.0, 5.0, 180.0, 0.5, "aggressive", 3000.0)

        desc_slow = generator._generate_audio_description(segment_slow, "calm", "ambient")
        desc_moderate = generator._generate_audio_description(segment_moderate, "happy", "pop")
        desc_fast = generator._generate_audio_description(segment_fast, "energetic", "rock")
        desc_very_fast = generator._generate_audio_description(segment_very_fast, "aggressive", "electronic")

        assert "slow" in desc_slow
        assert "moderate" in desc_moderate
        assert "fast" in desc_fast
        assert "very fast" in desc_very_fast

    def test_generate_negative_prompt_base_negatives(self):
        generator = PromptGenerator()

        negative = generator._generate_negative_prompt("happy")

        assert "low quality" in negative
        assert "blurry" in negative
        assert "distorted" in negative
        assert "watermark" in negative

    def test_generate_negative_prompt_mood_specific_calm(self):
        generator = PromptGenerator()

        negative = generator._generate_negative_prompt("calm")

        assert "chaotic" in negative
        assert "violent" in negative
        assert "aggressive movement" in negative

    def test_generate_negative_prompt_mood_specific_energetic(self):
        generator = PromptGenerator()

        negative = generator._generate_negative_prompt("energetic")

        assert "static" in negative
        assert "boring" in negative
        assert "slow" in negative

    def test_generate_negative_prompt_unknown_mood(self):
        generator = PromptGenerator()

        negative = generator._generate_negative_prompt("unknown_mood")

        assert "low quality" in negative
        assert "blurry" in negative

    def test_extract_visual_from_lyrics_sky(self):
        generator = PromptGenerator()

        lyrics = "Look at the beautiful sky above"
        visual = generator._extract_visual_from_lyrics(lyrics)

        assert visual is not None
        assert "expansive sky views" in visual

    def test_extract_visual_from_lyrics_multiple_keywords(self):
        generator = PromptGenerator()

        lyrics = "Dancing under the stars with fire in the night"
        visual = generator._extract_visual_from_lyrics(lyrics)

        assert visual is not None
        assert "starry night sky" in visual or "flame elements" in visual or "nighttime setting" in visual

    def test_extract_visual_from_lyrics_no_keywords(self):
        generator = PromptGenerator()

        lyrics = "This text has no visual keywords"
        visual = generator._extract_visual_from_lyrics(lyrics)

        assert visual is None

    def test_extract_visual_from_lyrics_empty(self):
        generator = PromptGenerator()

        visual = generator._extract_visual_from_lyrics("")

        assert visual is None

    def test_extract_visual_from_lyrics_none(self):
        generator = PromptGenerator()

        visual = generator._extract_visual_from_lyrics(None)

        assert visual is None

    def test_extract_visual_from_lyrics_limits_to_three(self):
        generator = PromptGenerator()

        lyrics = "sky sun moon star rain fire ocean sea"
        visual = generator._extract_visual_from_lyrics(lyrics)

        assert visual is not None
        visual_parts = visual.split(", ")
        assert len(visual_parts) <= 3

    def test_extract_visual_from_lyrics_case_insensitive(self):
        generator = PromptGenerator()

        lyrics = "THE OCEAN AND THE SKY"
        visual = generator._extract_visual_from_lyrics(lyrics)

        assert visual is not None
        assert "ocean waves" in visual or "expansive sky views" in visual

    def test_create_ovi_prompt(self):
        generator = PromptGenerator()

        video_prompt = VideoPrompt(
            segment_index=0,
            start_time=0.0,
            end_time=5.0,
            prompt_text="Beautiful sunset scene, cinematic quality",
            audio_description="Audio: energetic pop music with fast tempo",
            negative_prompt="low quality, blurry"
        )

        ovi_prompt = generator.create_ovi_prompt(video_prompt)

        assert video_prompt.prompt_text in ovi_prompt
        assert video_prompt.audio_description in ovi_prompt
        assert "\n\n" in ovi_prompt

    def test_prompt_includes_cinematic_elements(self):
        generator = PromptGenerator()

        segment = AudioSegment(
            start_time=0.0,
            end_time=5.0,
            tempo=120.0,
            energy=0.6,
            mood="happy",
            dominant_frequency=2000.0
        )

        prompt = generator._generate_segment_prompt(
            segment=segment,
            segment_index=0,
            overall_mood="happy",
            genre="pop"
        )

        assert "cinematic quality" in prompt.prompt_text
        assert "high production value" in prompt.prompt_text
        assert "professional lighting" in prompt.prompt_text

    def test_prompt_includes_mood_atmosphere(self):
        generator = PromptGenerator()

        segment = AudioSegment(
            start_time=0.0,
            end_time=5.0,
            tempo=100.0,
            energy=0.4,
            mood="mysterious",
            dominant_frequency=1500.0
        )

        prompt = generator._generate_segment_prompt(
            segment=segment,
            segment_index=0,
            overall_mood="mysterious",
            genre="ambient"
        )

        assert "mysterious atmosphere" in prompt.prompt_text

    @patch('random.choice')
    def test_random_selection_calls(self, mock_choice):
        mock_choice.side_effect = lambda x: x[0]

        generator = PromptGenerator()

        segment = AudioSegment(
            start_time=0.0,
            end_time=5.0,
            tempo=120.0,
            energy=0.5,
            mood="calm",
            dominant_frequency=1500.0
        )

        generator._generate_segment_prompt(
            segment=segment,
            segment_index=0,
            overall_mood="calm",
            genre="ambient"
        )

        assert mock_choice.call_count >= 3
