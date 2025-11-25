"""
Color manipulation utilities for Stegosuite.

Provides RGB channel operations and color distance calculations.
"""

from typing import Tuple, Union
import numpy as np


def rgb_to_tuple(rgb: int) -> Tuple[int, int, int]:
    """
    Convert RGB integer to (R, G, B) tuple.

    Args:
        rgb: RGB value as 24-bit integer (0xRRGGBB)

    Returns:
        Tuple of (red, green, blue) values
    """
    r = (rgb >> 16) & 0xFF
    g = (rgb >> 8) & 0xFF
    b = rgb & 0xFF
    return (r, g, b)


def tuple_to_rgb(r: int, g: int, b: int) -> int:
    """
    Convert (R, G, B) tuple to RGB integer.

    Args:
        r: Red value (0-255)
        g: Green value (0-255)
        b: Blue value (0-255)

    Returns:
        RGB value as 24-bit integer (0xRRGGBB)
    """
    return ((r & 0xFF) << 16) | ((g & 0xFF) << 8) | (b & 0xFF)


def euclidean_distance(color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> float:
    """
    Calculate Euclidean distance between two RGB colors.

    Args:
        color1: (R, G, B) tuple
        color2: (R, G, B) tuple

    Returns:
        Euclidean distance
    """
    r_diff = color1[0] - color2[0]
    g_diff = color1[1] - color2[1]
    b_diff = color1[2] - color2[2]
    return (r_diff ** 2 + g_diff ** 2 + b_diff ** 2) ** 0.5


def manhattan_distance(color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> int:
    """
    Calculate Manhattan distance between two RGB colors.

    Args:
        color1: (R, G, B) tuple
        color2: (R, G, B) tuple

    Returns:
        Manhattan distance
    """
    return abs(color1[0] - color2[0]) + abs(color1[1] - color2[1]) + abs(color1[2] - color2[2])


def is_homogeneous(pixels: list, threshold: int = 10) -> bool:
    """
    Check if a set of pixels represents a homogeneous (flat) region.
    Legacy function - use is_homogeneous_fast for better performance.

    Args:
        pixels: List of (R, G, B) tuples
        threshold: Maximum allowed color distance for homogeneous region

    Returns:
        True if region is homogeneous, False otherwise
    """
    if len(pixels) < 2:
        return True

    max_distance = 0
    for i in range(len(pixels)):
        for j in range(i + 1, len(pixels)):
            distance = manhattan_distance(pixels[i], pixels[j])
            max_distance = max(max_distance, distance)

    return max_distance <= threshold


def is_homogeneous_fast(neighborhood: np.ndarray, threshold: int = 10) -> bool:
    """
    Check if a neighborhood is homogeneous using O(n) min-max approach.
    
    This is much faster than is_homogeneous() which uses O(n^2) pairwise comparisons.
    The maximum Manhattan distance between any two pixels is bounded by the sum of
    (max - min) across all channels.

    Args:
        neighborhood: 2D or 3D numpy array of pixels (HxWx3 for RGB, HxW for grayscale)
        threshold: Maximum allowed color range for homogeneous region

    Returns:
        True if region is homogeneous, False otherwise
    """
    if neighborhood.size < 2:
        return True

    # Handle different array shapes
    if len(neighborhood.shape) == 3:
        # RGB image: flatten to (N, channels)
        flat = neighborhood.reshape(-1, neighborhood.shape[-1])
        # O(n) approach: sum of per-channel ranges bounds the max Manhattan distance
        channel_ranges = np.max(flat, axis=0) - np.min(flat, axis=0)
        total_range = int(np.sum(channel_ranges))
    elif len(neighborhood.shape) == 2:
        # Grayscale or already flattened
        total_range = int(np.max(neighborhood) - np.min(neighborhood))
    else:
        # 1D array
        total_range = int(np.max(neighborhood) - np.min(neighborhood))

    return total_range <= threshold


def grayscale(r: int, g: int, b: int) -> int:
    """
    Convert RGB to grayscale value.

    Args:
        r: Red value (0-255)
        g: Green value (0-255)
        b: Blue value (0-255)

    Returns:
        Grayscale value (0-255)
    """
    return int(0.299 * r + 0.587 * g + 0.114 * b)
