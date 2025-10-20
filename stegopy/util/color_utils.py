"""
Color manipulation utilities for Stegosuite.

Provides RGB channel operations and color distance calculations.
"""

from typing import Tuple


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
