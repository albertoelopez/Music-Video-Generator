import pytest
from pathlib import Path
from unittest.mock import patch, Mock

from src.utils.file_utils import (
    validate_audio_file,
    get_supported_formats,
    ensure_directory,
    get_unique_filename,
    clean_temp_files,
    get_file_info,
    SUPPORTED_AUDIO_FORMATS,
    SUPPORTED_VIDEO_FORMATS
)


class TestValidateAudioFile:
    def test_validate_audio_file_success(self, tmp_path):
        audio_file = tmp_path / "test.mp3"
        audio_file.write_bytes(b"fake audio content")

        valid, error = validate_audio_file(str(audio_file))

        assert valid is True
        assert error is None

    def test_validate_audio_file_not_found(self):
        valid, error = validate_audio_file("/nonexistent/file.mp3")

        assert valid is False
        assert "File not found" in error

    def test_validate_audio_file_not_a_file(self, tmp_path):
        directory = tmp_path / "testdir"
        directory.mkdir()

        valid, error = validate_audio_file(str(directory))

        assert valid is False
        assert "Not a file" in error

    def test_validate_audio_file_unsupported_format(self, tmp_path):
        invalid_file = tmp_path / "test.txt"
        invalid_file.write_bytes(b"not audio")

        valid, error = validate_audio_file(str(invalid_file))

        assert valid is False
        assert "Unsupported audio format" in error

    def test_validate_audio_file_empty(self, tmp_path):
        empty_file = tmp_path / "empty.mp3"
        empty_file.write_bytes(b"")

        valid, error = validate_audio_file(str(empty_file))

        assert valid is False
        assert "File is empty" in error

    def test_validate_audio_file_too_large(self, tmp_path):
        large_file = tmp_path / "large.wav"
        large_file.write_bytes(b"x" * (501 * 1024 * 1024))

        valid, error = validate_audio_file(str(large_file))

        assert valid is False
        assert "File too large" in error
        assert "500MB" in error

    def test_validate_audio_file_all_supported_formats(self, tmp_path):
        for fmt in SUPPORTED_AUDIO_FORMATS:
            audio_file = tmp_path / f"test{fmt}"
            audio_file.write_bytes(b"fake audio")

            valid, error = validate_audio_file(str(audio_file))

            assert valid is True
            assert error is None

    def test_validate_audio_file_case_insensitive(self, tmp_path):
        audio_file = tmp_path / "test.MP3"
        audio_file.write_bytes(b"fake audio")

        valid, error = validate_audio_file(str(audio_file))

        assert valid is True
        assert error is None


class TestGetSupportedFormats:
    def test_get_supported_formats_structure(self):
        formats = get_supported_formats()

        assert "audio" in formats
        assert "video" in formats
        assert isinstance(formats["audio"], list)
        assert isinstance(formats["video"], list)

    def test_get_supported_formats_audio(self):
        formats = get_supported_formats()

        assert ".mp3" in formats["audio"]
        assert ".wav" in formats["audio"]
        assert ".flac" in formats["audio"]

    def test_get_supported_formats_video(self):
        formats = get_supported_formats()

        assert ".mp4" in formats["video"]
        assert ".avi" in formats["video"]
        assert ".mov" in formats["video"]


class TestEnsureDirectory:
    def test_ensure_directory_creates_new(self, tmp_path):
        new_dir = tmp_path / "new_directory"

        result = ensure_directory(str(new_dir))

        assert Path(result).exists()
        assert Path(result).is_dir()

    def test_ensure_directory_exists_already(self, tmp_path):
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()

        result = ensure_directory(str(existing_dir))

        assert Path(result).exists()
        assert Path(result).is_dir()

    def test_ensure_directory_creates_parents(self, tmp_path):
        nested_dir = tmp_path / "parent" / "child" / "grandchild"

        result = ensure_directory(str(nested_dir))

        assert Path(result).exists()
        assert Path(result).is_dir()
        assert (tmp_path / "parent").exists()
        assert (tmp_path / "parent" / "child").exists()

    def test_ensure_directory_returns_string(self, tmp_path):
        new_dir = tmp_path / "test_dir"

        result = ensure_directory(str(new_dir))

        assert isinstance(result, str)


class TestGetUniqueFilename:
    def test_get_unique_filename_first_available(self, tmp_path):
        result = get_unique_filename(str(tmp_path), "test", ".txt")

        expected = tmp_path / "test.txt"
        assert result == str(expected)

    def test_get_unique_filename_increments(self, tmp_path):
        (tmp_path / "test.txt").touch()

        result = get_unique_filename(str(tmp_path), "test", ".txt")

        expected = tmp_path / "test_1.txt"
        assert result == str(expected)

    def test_get_unique_filename_multiple_increments(self, tmp_path):
        (tmp_path / "video.mp4").touch()
        (tmp_path / "video_1.mp4").touch()
        (tmp_path / "video_2.mp4").touch()

        result = get_unique_filename(str(tmp_path), "video", ".mp4")

        expected = tmp_path / "video_3.mp4"
        assert result == str(expected)

    def test_get_unique_filename_different_extensions(self, tmp_path):
        (tmp_path / "file.txt").touch()

        result = get_unique_filename(str(tmp_path), "file", ".mp3")

        expected = tmp_path / "file.mp3"
        assert result == str(expected)


class TestCleanTempFiles:
    def test_clean_temp_files_removes_tmp(self, tmp_path):
        (tmp_path / "file1.tmp").touch()
        (tmp_path / "file2.tmp").touch()
        (tmp_path / "keep.txt").touch()

        removed = clean_temp_files(str(tmp_path))

        assert removed == 2
        assert not (tmp_path / "file1.tmp").exists()
        assert not (tmp_path / "file2.tmp").exists()
        assert (tmp_path / "keep.txt").exists()

    def test_clean_temp_files_custom_pattern(self, tmp_path):
        (tmp_path / "data.cache").touch()
        (tmp_path / "other.cache").touch()
        (tmp_path / "keep.txt").touch()

        removed = clean_temp_files(str(tmp_path), pattern="*.cache")

        assert removed == 2
        assert not (tmp_path / "data.cache").exists()
        assert (tmp_path / "keep.txt").exists()

    def test_clean_temp_files_empty_directory(self, tmp_path):
        removed = clean_temp_files(str(tmp_path))

        assert removed == 0

    def test_clean_temp_files_nonexistent_directory(self):
        removed = clean_temp_files("/nonexistent/directory")

        assert removed == 0

    def test_clean_temp_files_handles_permission_error(self, tmp_path):
        temp_file = tmp_path / "test.tmp"
        temp_file.touch()

        with patch('pathlib.Path.unlink', side_effect=OSError("Permission denied")):
            removed = clean_temp_files(str(tmp_path))

            assert removed == 0


class TestGetFileInfo:
    def test_get_file_info_existing_file(self, tmp_path):
        test_file = tmp_path / "test.mp3"
        test_file.write_bytes(b"x" * 1024)

        info = get_file_info(str(test_file))

        assert info["exists"] is True
        assert info["name"] == "test.mp3"
        assert info["stem"] == "test"
        assert info["extension"] == ".mp3"
        assert info["size_bytes"] == 1024
        assert info["size_mb"] == 1024 / (1024 * 1024)
        assert info["is_file"] is True
        assert info["is_dir"] is False

    def test_get_file_info_nonexistent_file(self):
        info = get_file_info("/nonexistent/file.txt")

        assert info["exists"] is False
        assert len(info) == 1

    def test_get_file_info_directory(self, tmp_path):
        test_dir = tmp_path / "testdir"
        test_dir.mkdir()

        info = get_file_info(str(test_dir))

        assert info["exists"] is True
        assert info["is_file"] is False
        assert info["is_dir"] is True

    def test_get_file_info_has_timestamps(self, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        info = get_file_info(str(test_file))

        assert "created" in info
        assert "modified" in info
        assert isinstance(info["created"], float)
        assert isinstance(info["modified"], float)

    def test_get_file_info_size_calculations(self, tmp_path):
        test_file = tmp_path / "large.dat"
        size_bytes = 5 * 1024 * 1024
        test_file.write_bytes(b"x" * size_bytes)

        info = get_file_info(str(test_file))

        assert info["size_bytes"] == size_bytes
        assert abs(info["size_mb"] - 5.0) < 0.01


class TestConstants:
    def test_supported_audio_formats_list(self):
        assert isinstance(SUPPORTED_AUDIO_FORMATS, list)
        assert len(SUPPORTED_AUDIO_FORMATS) > 0
        assert all(fmt.startswith('.') for fmt in SUPPORTED_AUDIO_FORMATS)

    def test_supported_video_formats_list(self):
        assert isinstance(SUPPORTED_VIDEO_FORMATS, list)
        assert len(SUPPORTED_VIDEO_FORMATS) > 0
        assert all(fmt.startswith('.') for fmt in SUPPORTED_VIDEO_FORMATS)

    def test_no_duplicate_formats(self):
        assert len(SUPPORTED_AUDIO_FORMATS) == len(set(SUPPORTED_AUDIO_FORMATS))
        assert len(SUPPORTED_VIDEO_FORMATS) == len(set(SUPPORTED_VIDEO_FORMATS))
