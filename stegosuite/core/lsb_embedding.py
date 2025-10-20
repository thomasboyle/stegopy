"""
Modern LSB (Least Significant Bit) embedding for Stegosuite.

Implements a secure LSB-based algorithm that supports all image formats.
Uses pseudo-random pixel selection and multi-bit embedding for improved security.
"""

import numpy as np
from typing import List, Tuple, Optional
import hashlib

from stegosuite.core.embedding import EmbeddingMethod
from stegosuite.core.payload import Payload
from stegosuite.core.image_format import ImageFormat
from stegosuite.core.point_filter import PointFilter, NoFilter
from stegosuite.core.gpu_accelerator import get_accelerator
from stegosuite.util import byte_utils


class LSBEmbedding(EmbeddingMethod):
    """Modern LSB embedding supporting all image formats."""

    def __init__(self, image: ImageFormat, point_filter: PointFilter = None, key: str = ""):
        """Initialize LSB embedding.

        Args:
            image: ImageFormat instance
            point_filter: PointFilter instance (defaults to NoFilter)
            key: Key for pseudo-random pixel selection (defaults to empty)
        """
        super().__init__(image, point_filter or NoFilter())
        self.key = key or "default_lsb_key"
        self.bits_per_pixel = 1  # Use 1 LSB per channel for compatibility
        self._pixel_sequence = None
        self._gpu_accelerator = get_accelerator()

    def _generate_pixel_sequence(self, num_pixels: int) -> np.ndarray:
        """Generate pseudo-random sequence of pixel indices using GPU acceleration.

        Args:
            num_pixels: Total number of pixels to select from

        Returns:
            NumPy array of pixel indices in embedding order
        """
        if self._pixel_sequence is not None:
            return self._pixel_sequence

        # Use GPU accelerator for fast sequence generation
        sequence = self._gpu_accelerator.generate_pixel_sequence_vectorized(num_pixels, self.key)
        self._pixel_sequence = sequence
        return sequence

    def embed(self, payload: Payload) -> ImageFormat:
        """
        Embed payload using modern LSB algorithm.

        Args:
            payload: Payload to embed

        Returns:
            Modified image with embedded payload

        Raises:
            ValueError: If payload is too large
        """
        # Prepare payload
        payload_data = payload.pack_and_prepare()

        # Get image data
        pixels = self.image.get_pixel_array()
        height, width = pixels.shape[:2]
        total_pixels = height * width

        # Check capacity
        capacity = self.get_capacity()
        if len(payload_data) > capacity:
            raise ValueError(
                f"Payload too large: {len(payload_data)} bytes, but capacity is only {capacity} bytes"
            )

        # Generate pixel sequence using GPU acceleration
        pixel_sequence = self._generate_pixel_sequence(total_pixels)

        # Convert payload to bits using GPU accelerator
        bit_data = self._gpu_accelerator.bytes_to_bits_vectorized(payload_data)

        # Embed bits using parallel processing
        embedded_pixels = self._gpu_accelerator.embed_bits_parallel(
            pixels, bit_data, pixel_sequence, self.bits_per_pixel
        )

        # Update image with embedded pixels
        self.image.set_pixel_array(embedded_pixels.astype(np.uint8))
        return self.image

    def extract(self, password: str = "") -> Payload:
        """
        Extract payload from image using LSB algorithm.

        Args:
            password: Password for decryption (not used in extraction for LSB)

        Returns:
            Extracted payload

        Raises:
            ValueError: If extraction fails
        """
        pixels = self.image.get_pixel_array()
        height, width = pixels.shape[:2]
        total_pixels = height * width

        # Generate the same pixel sequence using GPU acceleration
        pixel_sequence = self._generate_pixel_sequence(total_pixels)

        # Calculate maximum possible bits we might need to extract
        # (we'll extract until we find valid payload data)

        # Extract bits using parallel processing
        extracted_bits = self._gpu_accelerator.extract_bits_parallel(
            pixels, pixel_sequence, total_pixels * (3 if len(pixels.shape) == 3 else 1), self.bits_per_pixel
        )

        # Convert bits to bytes using GPU accelerator
        extracted_data = self._gpu_accelerator.bits_to_bytes_vectorized(extracted_bits)

        # Unpack and extract payload
        blocks, _ = Payload.unpack_and_extract(bytes(extracted_data), password)

        # Create payload instance with extracted blocks
        payload = Payload(password)
        payload._extracted_blocks = blocks
        return payload

    def get_capacity(self) -> int:
        """Get maximum embedding capacity in bytes."""
        pixels = self.image.get_pixel_array()
        height, width = pixels.shape[:2]

        if len(pixels.shape) == 3:  # RGB image
            # 1 bit per channel per pixel
            total_bits = height * width * 3
        else:  # Grayscale image
            # 1 bit per pixel
            total_bits = height * width

        # Return capacity in bytes (bits // 8)
        return total_bits // 8
