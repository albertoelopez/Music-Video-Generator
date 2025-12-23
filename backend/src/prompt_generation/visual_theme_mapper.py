from typing import Dict, List, Tuple


class VisualThemeMapper:
    MOOD_TO_VISUALS: Dict[str, Dict[str, List[str]]] = {
        "energetic": {
            "scenes": [
                "neon-lit cityscape with pulsing lights",
                "dynamic crowd at a concert",
                "fast-moving cars with motion blur",
                "explosive fireworks display",
                "athletes in intense action"
            ],
            "colors": ["vibrant red", "electric blue", "neon pink", "bright yellow"],
            "movements": ["fast cuts", "rapid zoom", "spinning camera", "strobing lights"],
            "environments": ["urban streets", "stadium", "club", "race track"]
        },
        "calm": {
            "scenes": [
                "serene mountain lake at sunset",
                "gentle waves on a beach",
                "misty forest at dawn",
                "peaceful zen garden",
                "floating clouds over meadows"
            ],
            "colors": ["soft blue", "pale green", "warm beige", "gentle lavender"],
            "movements": ["slow pan", "gentle drift", "static wide shot", "subtle zoom"],
            "environments": ["nature", "beach", "garden", "countryside"]
        },
        "happy": {
            "scenes": [
                "sunny day in a flower field",
                "children playing in a park",
                "colorful carnival celebration",
                "friends laughing together",
                "butterflies in a meadow"
            ],
            "colors": ["bright yellow", "cheerful orange", "sky blue", "grass green"],
            "movements": ["bouncy camera", "playful tracking", "joyful spin"],
            "environments": ["park", "beach", "festival", "garden"]
        },
        "sad": {
            "scenes": [
                "rain falling on empty streets",
                "solitary figure by a window",
                "autumn leaves falling",
                "abandoned places with memories",
                "foggy landscape at dusk"
            ],
            "colors": ["muted blue", "gray", "desaturated tones", "cold white"],
            "movements": ["slow dolly", "lingering shots", "static contemplation"],
            "environments": ["rainy city", "empty room", "cemetery", "winter scene"]
        },
        "aggressive": {
            "scenes": [
                "lightning storm over dark landscape",
                "intense battle scene",
                "roaring flames and explosions",
                "heavy machinery in motion",
                "powerful waves crashing"
            ],
            "colors": ["deep red", "black", "metallic silver", "dark orange"],
            "movements": ["shaky cam", "aggressive cuts", "impact zooms"],
            "environments": ["battlefield", "industrial zone", "storm", "volcano"]
        },
        "dreamy": {
            "scenes": [
                "ethereal forest with floating particles",
                "surreal underwater world",
                "clouds morphing into shapes",
                "starfield with nebulae",
                "abstract light patterns"
            ],
            "colors": ["pastel purple", "soft pink", "iridescent", "translucent blue"],
            "movements": ["floating camera", "smooth glide", "dissolve transitions"],
            "environments": ["fantasy realm", "space", "underwater", "clouds"]
        },
        "mysterious": {
            "scenes": [
                "foggy alleyway with dim lights",
                "ancient temple ruins",
                "shadowy forest with glowing eyes",
                "noir cityscape at night",
                "hidden underground chambers"
            ],
            "colors": ["deep purple", "dark blue", "shadowy black", "dim amber"],
            "movements": ["slow reveal", "creeping zoom", "obscured angles"],
            "environments": ["dark forest", "old mansion", "underground", "foggy streets"]
        },
        "romantic": {
            "scenes": [
                "couple dancing under moonlight",
                "sunset over the ocean",
                "candlelit dinner scene",
                "cherry blossoms falling",
                "stargazing on a rooftop"
            ],
            "colors": ["rose pink", "warm gold", "soft red", "champagne"],
            "movements": ["graceful tracking", "intimate close-ups", "slow motion"],
            "environments": ["Paris streets", "beach sunset", "garden", "balcony"]
        },
        "epic": {
            "scenes": [
                "vast mountain range from aerial view",
                "armies marching across plains",
                "towering castle in the clouds",
                "massive space battle",
                "ancient civilization rising"
            ],
            "colors": ["royal gold", "deep blue", "crimson", "silver"],
            "movements": ["sweeping crane shots", "dramatic reveals", "slow motion impact"],
            "environments": ["mountains", "castle", "space", "ancient city"]
        },
        "playful": {
            "scenes": [
                "animated characters bouncing",
                "colorful candy world",
                "playful pets running",
                "carnival rides in motion",
                "bubble-filled environment"
            ],
            "colors": ["candy pink", "bright cyan", "sunny yellow", "lime green"],
            "movements": ["bouncy motion", "whip pans", "playful zooms"],
            "environments": ["playground", "toy store", "amusement park", "cartoon world"]
        }
    }

    GENRE_TO_AESTHETICS: Dict[str, Dict[str, List[str]]] = {
        "electronic": {
            "style": ["cyberpunk", "futuristic", "digital art", "glitch aesthetic"],
            "elements": ["circuit patterns", "LED grids", "holographic displays", "wireframe models"]
        },
        "rock": {
            "style": ["gritty", "raw", "rebellious", "concert footage style"],
            "elements": ["guitars", "amplifiers", "crowd surfing", "stage lights"]
        },
        "hip-hop": {
            "style": ["urban", "street art", "graffiti", "contemporary"],
            "elements": ["city skylines", "basketball courts", "lowriders", "boomboxes"]
        },
        "classical": {
            "style": ["elegant", "timeless", "orchestral", "painterly"],
            "elements": ["grand halls", "orchestras", "flowing fabrics", "nature scenes"]
        },
        "ambient": {
            "style": ["minimalist", "abstract", "ethereal", "atmospheric"],
            "elements": ["geometric shapes", "flowing particles", "light rays", "cosmic imagery"]
        },
        "pop": {
            "style": ["polished", "trendy", "vibrant", "mainstream appeal"],
            "elements": ["fashion", "dance", "bright sets", "modern aesthetics"]
        },
        "general": {
            "style": ["versatile", "balanced", "accessible"],
            "elements": ["mixed media", "varied scenes", "universal themes"]
        }
    }

    TEMPO_TO_PACING: Dict[str, Dict[str, any]] = {
        "slow": {
            "range": (0, 80),
            "cut_frequency": "long takes",
            "camera_speed": "slow and deliberate",
            "transition_style": "fade and dissolve"
        },
        "medium": {
            "range": (80, 120),
            "cut_frequency": "moderate cuts",
            "camera_speed": "steady movement",
            "transition_style": "mix of cuts and transitions"
        },
        "fast": {
            "range": (120, 160),
            "cut_frequency": "quick cuts",
            "camera_speed": "dynamic movement",
            "transition_style": "sharp cuts"
        },
        "very_fast": {
            "range": (160, 300),
            "cut_frequency": "rapid fire cuts",
            "camera_speed": "intense motion",
            "transition_style": "flash cuts and strobing"
        }
    }

    def get_visual_elements(self, mood: str) -> Dict[str, List[str]]:
        return self.MOOD_TO_VISUALS.get(mood, self.MOOD_TO_VISUALS["calm"])

    def get_genre_aesthetics(self, genre: str) -> Dict[str, List[str]]:
        return self.GENRE_TO_AESTHETICS.get(genre, self.GENRE_TO_AESTHETICS["general"])

    def get_tempo_pacing(self, tempo: float) -> Dict[str, any]:
        for pacing_name, pacing_info in self.TEMPO_TO_PACING.items():
            low, high = pacing_info["range"]
            if low <= tempo < high:
                return pacing_info
        return self.TEMPO_TO_PACING["medium"]

    def map_energy_to_intensity(self, energy: float) -> str:
        if energy < 0.3:
            return "subtle and understated"
        elif energy < 0.5:
            return "moderate presence"
        elif energy < 0.7:
            return "strong and impactful"
        else:
            return "intense and overwhelming"

    def get_color_grading(self, mood: str, genre: str) -> str:
        mood_colors = self.MOOD_TO_VISUALS.get(mood, {}).get("colors", [])
        if mood_colors:
            primary_color = mood_colors[0]
            return f"color graded with {primary_color} tones"
        return "balanced color grading"
