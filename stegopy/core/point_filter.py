"""
Point filter module for Stegosuite.

Filters pixels to avoid embedding in homogeneous (flat) regions of images.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple

import numpy as np

from stegopy.util import color_utils


class PointFilter(ABC):
    """Abstract base class for point filters."""

    @abstractmethod
    def should_embed(
        self, pixel_data: np.ndarray, x: int, y: int, neighborhood_size: int = 3
    ) -> bool:
        """
        Determine if a pixel should be used for embedding.

        Args:
            pixel_data: Full image pixel data (HxWx3)
            x: X coordinate
            y: Y coordinate
            neighborhood_size: Size of neighborhood to check

        Returns:
            True if pixel should be embedded, False otherwise
        """
        pass


class NoFilter(PointFilter):
    """Filter that allows embedding in all pixels."""

    def should_embed(
        self, pixel_data: np.ndarray, x: int, y: int, neighborhood_size: int = 3
    ) -> bool:
        """All pixels are valid for embedding."""
        return True


class HomogeneousFilter(PointFilter):
    """Filter that skips homogeneous (flat) regions."""

    def __init__(self, threshold: int = 30):
        """
        Initialize homogeneous filter.

        Args:
            threshold: Maximum color distance for homogeneous region
        """
        self.threshold = threshold

    def should_embed(
        self, pixel_data: np.ndarray, x: int, y: int, neighborhood_size: int = 3
    ) -> bool:
        """
        Check if pixel is in a non-homogeneous region.

        Skips embedding in flat areas with little color variation.
        """
        height, width = pixel_data.shape[:2]

        # Get neighborhood bounds
        half = neighborhood_size // 2
        y_start = max(0, y - half)
        y_end = min(height, y + half + 1)
        x_start = max(0, x - half)
        x_end = min(width, x + half + 1)

        # Get neighborhood pixels
        neighborhood = pixel_data[y_start:y_end, x_start:x_end]

        # Flatten to list of RGB tuples, ensuring proper conversion from NumPy arrays
        pixels = [
            tuple(int(c) for c in neighborhood[i, j]) 
            for i in range(neighborhood.shape[0]) 
            for j in range(neighborhood.shape[1])
        ]

        # Check if homogeneous
        return not color_utils.is_homogeneous(pixels, self.threshold)
