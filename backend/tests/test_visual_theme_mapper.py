import pytest
from src.prompt_generation.visual_theme_mapper import VisualThemeMapper


class TestVisualThemeMapper:
    def test_initialization(self):
        mapper = VisualThemeMapper()
        assert hasattr(mapper, 'MOOD_TO_VISUALS')
        assert hasattr(mapper, 'GENRE_TO_AESTHETICS')
        assert hasattr(mapper, 'TEMPO_TO_PACING')

    def test_get_visual_elements_valid_mood(self):
        mapper = VisualThemeMapper()
        elements = mapper.get_visual_elements("energetic")

        assert "scenes" in elements
        assert "colors" in elements
        assert "movements" in elements
        assert "environments" in elements
        assert isinstance(elements["scenes"], list)
        assert len(elements["scenes"]) > 0

    def test_get_visual_elements_invalid_mood_returns_calm(self):
        mapper = VisualThemeMapper()
        elements = mapper.get_visual_elements("nonexistent_mood")

        calm_elements = mapper.get_visual_elements("calm")
        assert elements == calm_elements

    def test_get_visual_elements_all_moods(self):
        mapper = VisualThemeMapper()
        moods = ["energetic", "calm", "happy", "sad", "aggressive", "dreamy", "mysterious", "romantic", "epic", "playful"]

        for mood in moods:
            elements = mapper.get_visual_elements(mood)
            assert "scenes" in elements
            assert "colors" in elements
            assert "movements" in elements
            assert "environments" in elements

    def test_get_genre_aesthetics_valid_genre(self):
        mapper = VisualThemeMapper()
        aesthetics = mapper.get_genre_aesthetics("electronic")

        assert "style" in aesthetics
        assert "elements" in aesthetics
        assert isinstance(aesthetics["style"], list)
        assert len(aesthetics["style"]) > 0

    def test_get_genre_aesthetics_invalid_genre_returns_general(self):
        mapper = VisualThemeMapper()
        aesthetics = mapper.get_genre_aesthetics("unknown_genre")

        general_aesthetics = mapper.get_genre_aesthetics("general")
        assert aesthetics == general_aesthetics

    def test_get_genre_aesthetics_all_genres(self):
        mapper = VisualThemeMapper()
        genres = ["electronic", "rock", "hip-hop", "classical", "ambient", "pop", "general"]

        for genre in genres:
            aesthetics = mapper.get_genre_aesthetics(genre)
            assert "style" in aesthetics
            assert "elements" in aesthetics

    def test_get_tempo_pacing_slow(self):
        mapper = VisualThemeMapper()
        pacing = mapper.get_tempo_pacing(60.0)

        assert pacing["cut_frequency"] == "long takes"
        assert pacing["camera_speed"] == "slow and deliberate"
        assert pacing["transition_style"] == "fade and dissolve"

    def test_get_tempo_pacing_medium(self):
        mapper = VisualThemeMapper()
        pacing = mapper.get_tempo_pacing(100.0)

        assert pacing["cut_frequency"] == "moderate cuts"
        assert pacing["camera_speed"] == "steady movement"

    def test_get_tempo_pacing_fast(self):
        mapper = VisualThemeMapper()
        pacing = mapper.get_tempo_pacing(140.0)

        assert pacing["cut_frequency"] == "quick cuts"
        assert pacing["camera_speed"] == "dynamic movement"

    def test_get_tempo_pacing_very_fast(self):
        mapper = VisualThemeMapper()
        pacing = mapper.get_tempo_pacing(180.0)

        assert pacing["cut_frequency"] == "rapid fire cuts"
        assert pacing["camera_speed"] == "intense motion"
        assert pacing["transition_style"] == "flash cuts and strobing"

    def test_get_tempo_pacing_boundary_values(self):
        mapper = VisualThemeMapper()

        pacing_79 = mapper.get_tempo_pacing(79.9)
        assert pacing_79["cut_frequency"] == "long takes"

        pacing_80 = mapper.get_tempo_pacing(80.0)
        assert pacing_80["cut_frequency"] == "moderate cuts"

        pacing_120 = mapper.get_tempo_pacing(120.0)
        assert pacing_120["cut_frequency"] == "quick cuts"

        pacing_160 = mapper.get_tempo_pacing(160.0)
        assert pacing_160["cut_frequency"] == "rapid fire cuts"

    def test_get_tempo_pacing_out_of_range_returns_medium(self):
        mapper = VisualThemeMapper()
        pacing = mapper.get_tempo_pacing(500.0)

        assert pacing["cut_frequency"] == "moderate cuts"

    def test_map_energy_to_intensity_subtle(self):
        mapper = VisualThemeMapper()
        intensity = mapper.map_energy_to_intensity(0.2)

        assert intensity == "subtle and understated"

    def test_map_energy_to_intensity_moderate(self):
        mapper = VisualThemeMapper()
        intensity = mapper.map_energy_to_intensity(0.4)

        assert intensity == "moderate presence"

    def test_map_energy_to_intensity_strong(self):
        mapper = VisualThemeMapper()
        intensity = mapper.map_energy_to_intensity(0.6)

        assert intensity == "strong and impactful"

    def test_map_energy_to_intensity_intense(self):
        mapper = VisualThemeMapper()
        intensity = mapper.map_energy_to_intensity(0.8)

        assert intensity == "intense and overwhelming"

    def test_map_energy_to_intensity_boundary_values(self):
        mapper = VisualThemeMapper()

        assert mapper.map_energy_to_intensity(0.0) == "subtle and understated"
        assert mapper.map_energy_to_intensity(0.29) == "subtle and understated"
        assert mapper.map_energy_to_intensity(0.3) == "moderate presence"
        assert mapper.map_energy_to_intensity(0.49) == "moderate presence"
        assert mapper.map_energy_to_intensity(0.5) == "strong and impactful"
        assert mapper.map_energy_to_intensity(0.69) == "strong and impactful"
        assert mapper.map_energy_to_intensity(0.7) == "intense and overwhelming"
        assert mapper.map_energy_to_intensity(1.0) == "intense and overwhelming"

    def test_get_color_grading_with_valid_mood(self):
        mapper = VisualThemeMapper()
        grading = mapper.get_color_grading("energetic", "electronic")

        assert "color graded with" in grading
        assert "vibrant red" in grading

    def test_get_color_grading_with_invalid_mood(self):
        mapper = VisualThemeMapper()
        grading = mapper.get_color_grading("invalid_mood", "pop")

        assert grading == "balanced color grading"

    def test_get_color_grading_mood_priority_over_genre(self):
        mapper = VisualThemeMapper()
        grading1 = mapper.get_color_grading("calm", "rock")
        grading2 = mapper.get_color_grading("aggressive", "classical")

        assert "soft blue" in grading1
        assert "deep red" in grading2

    def test_mood_to_visuals_structure(self):
        mapper = VisualThemeMapper()

        for mood, visuals in mapper.MOOD_TO_VISUALS.items():
            assert "scenes" in visuals
            assert "colors" in visuals
            assert "movements" in visuals
            assert "environments" in visuals
            assert len(visuals["scenes"]) > 0
            assert len(visuals["colors"]) > 0
            assert len(visuals["movements"]) > 0
            assert len(visuals["environments"]) > 0

    def test_genre_to_aesthetics_structure(self):
        mapper = VisualThemeMapper()

        for genre, aesthetics in mapper.GENRE_TO_AESTHETICS.items():
            assert "style" in aesthetics
            assert "elements" in aesthetics
            assert len(aesthetics["style"]) > 0
            assert len(aesthetics["elements"]) > 0

    def test_tempo_to_pacing_structure(self):
        mapper = VisualThemeMapper()

        for pacing_name, pacing_info in mapper.TEMPO_TO_PACING.items():
            assert "range" in pacing_info
            assert "cut_frequency" in pacing_info
            assert "camera_speed" in pacing_info
            assert "transition_style" in pacing_info
            assert isinstance(pacing_info["range"], tuple)
            assert len(pacing_info["range"]) == 2

    def test_tempo_ranges_do_not_overlap(self):
        mapper = VisualThemeMapper()

        ranges = []
        for pacing_info in mapper.TEMPO_TO_PACING.values():
            ranges.append(pacing_info["range"])

        ranges.sort()
        for i in range(len(ranges) - 1):
            assert ranges[i][1] <= ranges[i + 1][0]

    def test_all_moods_have_required_keys(self):
        mapper = VisualThemeMapper()
        required_keys = ["scenes", "colors", "movements", "environments"]

        for mood in mapper.MOOD_TO_VISUALS:
            for key in required_keys:
                assert key in mapper.MOOD_TO_VISUALS[mood]

    def test_all_genres_have_required_keys(self):
        mapper = VisualThemeMapper()
        required_keys = ["style", "elements"]

        for genre in mapper.GENRE_TO_AESTHETICS:
            for key in required_keys:
                assert key in mapper.GENRE_TO_AESTHETICS[genre]
