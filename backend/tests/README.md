# Backend Tests

Comprehensive test suite for the audio_to_musicvideo backend.

## Test Structure

```
tests/
├── conftest.py                    # Pytest fixtures and test configuration
├── test_audio_analyzer.py         # Tests for AudioAnalyzer class
├── test_beat_detector.py          # Tests for BeatDetector class
├── test_mood_classifier.py        # Tests for MoodClassifier class
├── test_prompt_generator.py       # Tests for PromptGenerator class
├── test_visual_theme_mapper.py    # Tests for VisualThemeMapper class
├── test_file_utils.py             # Tests for file utility functions
├── test_config.py                 # Tests for Config class
└── test_pipeline.py               # Tests for MusicVideoPipeline class
```

## Setup

1. Install test dependencies:
```bash
pip install -r requirements-test.txt
```

2. Ensure main dependencies are installed:
```bash
pip install -r requirements.txt
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=src --cov-report=html --cov-report=term
```

### Run specific test file
```bash
pytest tests/test_audio_analyzer.py
```

### Run specific test class
```bash
pytest tests/test_beat_detector.py::TestBeatDetector
```

### Run specific test
```bash
pytest tests/test_mood_classifier.py::TestMoodClassifier::test_classify_returns_mood
```

### Run tests in parallel
```bash
pytest -n auto
```

### Run with verbose output
```bash
pytest -v
```

### Run only failed tests from last run
```bash
pytest --lf
```

## Test Coverage

The test suite covers:

### Audio Analysis
- AudioAnalyzer: Audio loading, analysis pipeline, genre prediction, segment creation
- BeatDetector: Beat detection, downbeat detection, tempo changes
- MoodClassifier: Mood classification, feature extraction, scoring algorithms

### Prompt Generation
- PromptGenerator: Prompt generation, style overrides, lyrics integration
- VisualThemeMapper: Visual element mapping, genre aesthetics, tempo pacing

### Utilities
- Config: Configuration loading, environment variables, directory management
- File Utils: File validation, directory operations, file info

### Pipeline
- MusicVideoPipeline: End-to-end workflow, progress tracking, error handling

## Writing New Tests

Follow these principles:

1. Use descriptive test names that explain what is being tested
2. Mock external dependencies (librosa, whisper, etc.)
3. Test edge cases and error conditions
4. Use fixtures from conftest.py for common test data
5. Follow the Arrange-Act-Assert pattern

Example:
```python
def test_feature_does_something(self, sample_audio_data):
    y, sr = sample_audio_data

    with patch('librosa.some_function') as mock_func:
        mock_func.return_value = expected_value

        result = function_under_test(y, sr)

        assert result == expected_result
```

## Fixtures

Common fixtures available in `conftest.py`:

- `sample_audio_data`: 10-second synthetic audio with 440Hz tone
- `short_audio_data`: 2-second synthetic audio
- `silence_audio_data`: 5 seconds of silence
- `high_energy_audio`: High frequency, high amplitude audio
- `low_energy_audio`: Low frequency, low amplitude audio
- `temp_audio_file`: Temporary WAV file
- `temp_dir`: Temporary directory
- `mock_whisper_model`: Mock Whisper model for lyrics extraction
- `sample_beat_times`: Sample beat time array
- `mock_config`: Mock configuration object

## Continuous Integration

Tests are designed to run in CI/CD environments. They:

- Do not require GPU
- Use mocks for heavy ML models
- Run quickly (< 60 seconds for full suite)
- Have no external dependencies

## Debugging Tests

To drop into debugger on failure:
```bash
pytest --pdb
```

To see print statements:
```bash
pytest -s
```

To see full traceback:
```bash
pytest --tb=long
```
