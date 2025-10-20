"""
Image utilities for Stegosuite.

Provides format detection, metadata extraction, and image validation.
"""

import os
from pathlib import Path
from typing import Optional, Tuple

from stegopy.config.constants import SUPPORTED_FORMATS


def detect_format(file_path: str) -> Optional[str]:
    """
    Detect image format from file path.

    Args:
        file_path: Path to image file

    Returns:
        Format string ('bmp', 'gif', 'jpg', 'jpeg', 'png') or None if unsupported

    Raises:
        FileNotFoundError: If file does not exist
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = Path(file_path).suffix.lower().lstrip(".")

    # Map common extensions
    if ext in ("jpg", "jpeg"):
        return "jpg"
    elif ext in SUPPORTED_FORMATS:
        return ext
    else:
        return None


def get_file_size(file_path: str) -> int:
    """
    Get file size in bytes.

    Args:
        file_path: Path to file

    Returns:
        File size in bytes

    Raises:
        FileNotFoundError: If file does not exist
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    return os.path.getsize(file_path)


def get_image_dimensions(image) -> Tuple[int, int]:
    """
    Get image dimensions (width, height).

    Args:
        image: PIL Image object

    Returns:
        Tuple of (width, height)
    """
    return image.size


def validate_image_format(file_path: str) -> Tuple[bool, str]:
    """
    Validate that file is a supported image format.

    Args:
        file_path: Path to image file

    Returns:
        Tuple of (is_valid, message)
    """
    if not os.path.exists(file_path):
        return (False, "File does not exist")

    format_detected = detect_format(file_path)
    if not format_detected:
        return (False, "Unsupported image format")

    return (True, f"Valid {format_detected.upper()} image")


def get_output_path(input_path: str, suffix: str = "_stego") -> str:
    """
    Generate output file path for embedded image.

    Args:
        input_path: Original image path
        suffix: Suffix to add before extension

    Returns:
        Output file path
    """
    path = Path(input_path)
    stem = path.stem
    suffix_str = f"{stem}{suffix}"
    return str(path.parent / f"{suffix_str}{path.suffix}")


def get_extract_output_dir(image_path: str, create: bool = True) -> str:
    """
    Get directory for extracted files.

    Args:
        image_path: Path to stego image
        create: Whether to create directory if it doesn't exist

    Returns:
        Output directory path

    Raises:
        OSError: If directory creation fails
    """
    path = Path(image_path)
    output_dir = path.parent / f"{path.stem}_extracted"

    if create and not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    return str(output_dir)
