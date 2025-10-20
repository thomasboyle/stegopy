"""
Embedding abstraction layer for Stegosuite.

Defines interface for different embedding methods.
"""

from abc import ABC, abstractmethod
from typing import Callable, Optional

from stegosuite.core.payload import Payload
from stegosuite.core.image_format import ImageFormat
from stegosuite.core.point_filter import PointFilter, NoFilter


class EmbeddingMethod(ABC):
    """Abstract base class for embedding methods."""

    def __init__(self, image: ImageFormat, point_filter: Optional[PointFilter] = None):
        """
        Initialize embedding method.

        Args:
            image: ImageFormat instance
            point_filter: PointFilter instance (defaults to NoFilter)
        """
        self.image = image
        self.point_filter = point_filter or NoFilter()
        self.progress_callback: Optional[Callable] = None

    @abstractmethod
    def embed(self, payload: Payload) -> ImageFormat:
        """
        Embed payload into image.

        Args:
            payload: Payload instance containing data to embed

        Returns:
            Modified ImageFormat with embedded data

        Raises:
            ValueError: If payload is too large or other embedding error
        """
        pass

    @abstractmethod
    def extract(self, password: str = "") -> Payload:
        """
        Extract payload from image.

        Args:
            password: Password for decryption (if needed)

        Returns:
            Extracted Payload instance

        Raises:
            ValueError: If extraction fails or data is corrupted
        """
        pass

    @abstractmethod
    def get_capacity(self) -> int:
        """
        Get maximum embedding capacity in bytes.

        Returns:
            Capacity in bytes
        """
        pass

    def set_progress_callback(self, callback: Optional[Callable]) -> None:
        """
        Set callback for progress updates.

        Callback should accept (current, total) integers representing bytes processed.
        """
        self.progress_callback = callback

    def _report_progress(self, current: int, total: int) -> None:
        """Report progress to callback if set."""
        if self.progress_callback:
            self.progress_callback(current, total)
