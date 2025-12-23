import os
from pathlib import Path
from typing import List, Tuple, Optional


SUPPORTED_AUDIO_FORMATS = ['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac']
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.webm']


def validate_audio_file(file_path: str) -> Tuple[bool, Optional[str]]:
    path = Path(file_path)

    if not path.exists():
        return False, f"File not found: {file_path}"

    if not path.is_file():
        return False, f"Not a file: {file_path}"

    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_AUDIO_FORMATS:
        return False, f"Unsupported audio format: {suffix}. Supported formats: {SUPPORTED_AUDIO_FORMATS}"

    file_size = path.stat().st_size
    if file_size == 0:
        return False, "File is empty"

    max_size = 500 * 1024 * 1024
    if file_size > max_size:
        return False, f"File too large: {file_size / 1024 / 1024:.1f}MB. Maximum size: 500MB"

    return True, None


def get_supported_formats() -> dict:
    return {
        "audio": SUPPORTED_AUDIO_FORMATS,
        "video": SUPPORTED_VIDEO_FORMATS
    }


def ensure_directory(dir_path: str) -> str:
    path = Path(dir_path)
    path.mkdir(parents=True, exist_ok=True)
    return str(path)


def get_unique_filename(directory: str, base_name: str, extension: str) -> str:
    dir_path = Path(directory)
    counter = 0

    while True:
        if counter == 0:
            filename = f"{base_name}{extension}"
        else:
            filename = f"{base_name}_{counter}{extension}"

        full_path = dir_path / filename
        if not full_path.exists():
            return str(full_path)
        counter += 1


def clean_temp_files(directory: str, pattern: str = "*.tmp") -> int:
    import glob

    dir_path = Path(directory)
    if not dir_path.exists():
        return 0

    removed = 0
    for file_path in dir_path.glob(pattern):
        try:
            file_path.unlink()
            removed += 1
        except OSError:
            pass

    return removed


def get_file_info(file_path: str) -> dict:
    path = Path(file_path)

    if not path.exists():
        return {"exists": False}

    stat = path.stat()

    return {
        "exists": True,
        "name": path.name,
        "stem": path.stem,
        "extension": path.suffix,
        "size_bytes": stat.st_size,
        "size_mb": stat.st_size / (1024 * 1024),
        "created": stat.st_ctime,
        "modified": stat.st_mtime,
        "is_file": path.is_file(),
        "is_dir": path.is_dir()
    }
