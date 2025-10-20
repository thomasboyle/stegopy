"""
Image format handler for Stegosuite.

Unified interface for loading and manipulating different image formats.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from PIL import Image
import numpy as np

from stegopy.util import image_utils


class ImageFormat(ABC):
    """Abstract base class for image formats."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.image = Image.open(file_path)
        self.width, self.height = self.image.size
        self.format = self.image.format.lower() if self.image.format else "unknown"

    @abstractmethod
    def get_pixel_array(self) -> np.ndarray:
        """Get pixel array as numpy array."""
        pass

    @abstractmethod
    def set_pixel_array(self, array: np.ndarray) -> None:
        """Set pixel array from numpy array."""
        pass

    @abstractmethod
    def save(self, output_path: str, quality: Optional[int] = None) -> None:
        """Save image to file."""
        pass

    def get_capacity_estimate(self) -> int:
        """
        Estimate maximum payload capacity in bytes.

        Returns:
            Estimated capacity in bytes
        """
        raise NotImplementedError

    def close(self) -> None:
        """Close image resources."""
        if self.image:
            self.image.close()


class BMPImage(ImageFormat):
    """BMP image format handler."""

    def get_pixel_array(self) -> np.ndarray:
        """Get pixel array for BMP."""
        if self.image.mode != "RGB":
            self.image = self.image.convert("RGB")
        return np.array(self.image)

    def set_pixel_array(self, array: np.ndarray) -> None:
        """Set pixel array for BMP."""
        self.image = Image.fromarray(array.astype("uint8"), mode="RGB")

    def save(self, output_path: str, quality: Optional[int] = None) -> None:
        """Save BMP image."""
        if self.image.mode != "RGB":
            self.image = self.image.convert("RGB")
        self.image.save(output_path, format="BMP")

    def get_capacity_estimate(self) -> int:
        """Estimate BMP capacity (2 bits per pixel pair, ~25% of image size)."""
        pixel_count = self.width * self.height
        return (pixel_count * 3) // 8  # 3 channels, 2 bits per pixel


class GIFImage(ImageFormat):
    """GIF image format handler."""

    def get_pixel_array(self) -> np.ndarray:
        """Get pixel array for GIF."""
        if self.image.mode != "RGB":
            self.image = self.image.convert("RGB")
        return np.array(self.image)

    def set_pixel_array(self, array: np.ndarray) -> None:
        """Set pixel array for GIF."""
        self.image = Image.fromarray(array.astype("uint8"), mode="RGB")

    def save(self, output_path: str, quality: Optional[int] = None) -> None:
        """Save GIF image."""
        if self.image.mode != "RGB":
            self.image = self.image.convert("RGB")
        self.image.save(output_path, format="GIF")

    def get_capacity_estimate(self) -> int:
        """Estimate GIF capacity (2 bits per pixel pair)."""
        pixel_count = self.width * self.height
        return (pixel_count * 3) // 8


class JPGImage(ImageFormat):
    """JPEG image format handler."""

    def get_pixel_array(self) -> np.ndarray:
        """Get pixel array for JPEG."""
        if self.image.mode != "RGB":
            self.image = self.image.convert("RGB")
        return np.array(self.image)

    def set_pixel_array(self, array: np.ndarray) -> None:
        """Set pixel array for JPEG."""
        self.image = Image.fromarray(array.astype("uint8"), mode="RGB")

    def save(self, output_path: str, quality: Optional[int] = None) -> None:
        """Save JPEG image with specified quality."""
        if self.image.mode != "RGB":
            self.image = self.image.convert("RGB")
        if quality is None:
            quality = 95
        self.image.save(output_path, format="JPEG", quality=quality)

    def get_capacity_estimate(self) -> int:
        """Estimate JPEG capacity (DCT-based, ~15-20% of image size)."""
        pixel_count = self.width * self.height
        return (pixel_count * 2) // 8


class PNGImage(ImageFormat):
    """PNG image format handler."""

    def get_pixel_array(self) -> np.ndarray:
        """Get pixel array for PNG."""
        if self.image.mode != "RGB":
            self.image = self.image.convert("RGB")
        return np.array(self.image)

    def set_pixel_array(self, array: np.ndarray) -> None:
        """Set pixel array for PNG."""
        self.image = Image.fromarray(array.astype("uint8"), mode="RGB")

    def save(self, output_path: str, quality: Optional[int] = None) -> None:
        """Save PNG image with no compression to preserve embedded data."""
        if self.image.mode != "RGB":
            self.image = self.image.convert("RGB")
        # Use compress_level=0 to disable PNG filters that can corrupt embedded data
        self.image.save(output_path, format="PNG", compress_level=0, optimize=False)

    def get_capacity_estimate(self) -> int:
        """Estimate PNG capacity (2 bits per pixel pair)."""
        pixel_count = self.width * self.height
        return (pixel_count * 3) // 8


def load_image(file_path: str) -> ImageFormat:
    """
    Load an image file and return appropriate ImageFormat handler.

    Args:
        file_path: Path to image file

    Returns:
        ImageFormat subclass instance

    Raises:
        ValueError: If format is not supported
        FileNotFoundError: If file does not exist
    """
    format_detected = image_utils.detect_format(file_path)

    if format_detected == "bmp":
        return BMPImage(file_path)
    elif format_detected == "gif":
        return GIFImage(file_path)
    elif format_detected == "jpg":
        return JPGImage(file_path)
    elif format_detected == "png":
        return PNGImage(file_path)
    else:
        raise ValueError(f"Unsupported image format: {format_detected}")
