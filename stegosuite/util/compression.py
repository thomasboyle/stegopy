"""
Compression utilities for Stegosuite.

Handles zlib compression and decompression of payload data.
"""

import zlib


def compress(data: bytes) -> bytes:
    """
    Compress data using zlib.

    Args:
        data: Data to compress

    Returns:
        Compressed data

    Raises:
        ValueError: If compression fails
    """
    try:
        return zlib.compress(data, level=9)
    except Exception as e:
        raise ValueError(f"Compression failed: {str(e)}")


def decompress(compressed_data: bytes) -> bytes:
    """
    Decompress data compressed with compress().

    Args:
        compressed_data: Compressed data

    Returns:
        Decompressed data

    Raises:
        ValueError: If decompression fails
    """
    try:
        return zlib.decompress(compressed_data)
    except Exception as e:
        raise ValueError(f"Decompression failed: {str(e)}")
