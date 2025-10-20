"""
Pixel Value Differencing (PVD) embedding for Stegosuite.

Implements PVD embedding for BMP, GIF, and PNG formats.
"""

import numpy as np
from typing import List, Tuple

from stegopy.core.embedding import EmbeddingMethod
from stegopy.core.payload import Payload
from stegopy.core.image_format import ImageFormat
from stegopy.core.point_filter import PointFilter, NoFilter
from stegopy.util import byte_utils
from stegopy.config.constants import PVD_RANGES


class PVDEmbedding(EmbeddingMethod):
    """Pixel Value Differencing embedding for raster formats."""

    def __init__(self, image: ImageFormat, point_filter: PointFilter = None):
        """Initialize PVD embedding."""
        super().__init__(image, point_filter or NoFilter())
        self.pvd_ranges = PVD_RANGES

    def embed(self, payload: Payload) -> ImageFormat:
        """
        Embed payload using PVD algorithm.

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

        # Check capacity
        capacity = self.get_capacity()
        if len(payload_data) > capacity:
            raise ValueError(
                f"Payload too large: {len(payload_data)} bytes, but capacity is only {capacity} bytes"
            )

        # Embed payload bits
        bit_index = 0
        bit_data = byte_utils.iterate_bits(payload_data)
        bits_embedded_total = 0

        embedded_pixels = pixels.copy()

        for y in range(height - 1):
            for x in range(0, width - 1):
                # Skip if filter says to
                if not self.point_filter.should_embed(pixels, x, y):
                    continue

                # Process R channel pair
                r1 = int(embedded_pixels[y, x, 0])
                r2 = int(embedded_pixels[y, x + 1, 0])
                bits_embedded = self._embed_pair(r1, r2, bit_data)
                if bits_embedded > 0:
                    embedded_pixels[y, x, 0], embedded_pixels[y, x + 1, 0] = self._get_modified_pair()
                    bits_embedded_total += bits_embedded

                # Process G channel pair
                g1 = int(embedded_pixels[y, x, 1])
                g2 = int(embedded_pixels[y, x + 1, 1])
                bits_embedded = self._embed_pair(g1, g2, bit_data)
                if bits_embedded > 0:
                    embedded_pixels[y, x, 1], embedded_pixels[y, x + 1, 1] = self._get_modified_pair()
                    bits_embedded_total += bits_embedded

                # Process B channel pair
                b1 = int(embedded_pixels[y, x, 2])
                b2 = int(embedded_pixels[y, x + 1, 2])
                bits_embedded = self._embed_pair(b1, b2, bit_data)
                if bits_embedded > 0:
                    embedded_pixels[y, x, 2], embedded_pixels[y, x + 1, 2] = self._get_modified_pair()
                    bits_embedded_total += bits_embedded

                # Report progress
                if bit_index % 1000 == 0:
                    self._report_progress(bit_index // 8, len(payload_data))

        # Update image with embedded pixels
        self.image.set_pixel_array(embedded_pixels)
        return self.image

    def extract(self, password: str = "") -> Payload:
        """
        Extract payload from image using PVD algorithm.

        Args:
            password: Password for decryption

        Returns:
            Extracted payload

        Raises:
            ValueError: If extraction fails
        """
        pixels = self.image.get_pixel_array()
        height, width = pixels.shape[:2]

        # Extract bits
        extracted_bits = []

        for y in range(height - 1):
            for x in range(0, width - 1):
                # Skip if filter says to
                if not self.point_filter.should_embed(pixels, x, y):
                    continue

                # Extract from R channel
                r1 = int(pixels[y, x, 0])
                r2 = int(pixels[y, x + 1, 0])
                bits = self._extract_pair(r1, r2)
                extracted_bits.extend(bits)

                # Extract from G channel
                g1 = int(pixels[y, x, 1])
                g2 = int(pixels[y, x + 1, 1])
                bits = self._extract_pair(g1, g2)
                extracted_bits.extend(bits)

                # Extract from B channel
                b1 = int(pixels[y, x, 2])
                b2 = int(pixels[y, x + 1, 2])
                bits = self._extract_pair(b1, b2)
                extracted_bits.extend(bits)

        # Convert bits to bytes
        extracted_data = bytearray()
        for i in range(0, len(extracted_bits) - 7, 8):
            byte_bits = extracted_bits[i : i + 8]
            byte_value = byte_utils.bits_to_byte(byte_bits)
            extracted_data.append(byte_value)

        # Unpack and extract payload
        blocks, _ = Payload.unpack_and_extract(bytes(extracted_data), password)

        # Create payload instance with extracted blocks
        payload = Payload(password)
        # Store blocks in payload for access
        payload._extracted_blocks = blocks
        return payload

    def get_capacity(self) -> int:
        """Get maximum embedding capacity in bytes."""
        pixels = self.image.get_pixel_array()
        height, width = pixels.shape[:2]

        # Conservative estimate: 1-2 bits per pixel pair per channel
        # For 3 channels: 3-6 bits per horizontal pixel pair
        # Approximate to 1.5 bits per pixel on average
        pixel_count = height * (width - 1)
        capacity = (pixel_count * 4) // 8  # 1.5 bits per pixel

        return capacity

    def _embed_pair(self, pixel1: int, pixel2: int, bit_stream) -> int:
        """Embed bits in a pixel pair. Store internally for modification."""
        self._p1 = pixel1
        self._p2 = pixel2
        d = abs(pixel1 - pixel2)

        # Find range for this difference
        for bits_count, (low, high) in enumerate(self.pvd_ranges):
            if low <= d <= high:
                # Determine bits to embed in this range
                if bits_count == 0:
                    # Range (0,1): embed 1 bit
                    bits_to_embed = 1
                else:
                    # Range with capacity for 2 bits
                    bits_to_embed = 2

                # Get bits from stream
                embedded_bits = []
                for _ in range(bits_to_embed):
                    try:
                        bit = next(bit_stream)
                        embedded_bits.append(bit)
                    except StopIteration:
                        return 0

                # Modify pixels based on embedded bits
                secret_value = sum(b << i for i, b in enumerate(embedded_bits))
                new_d = low + (secret_value % (high - low + 1))

                # Update pixels to new difference
                if pixel1 >= pixel2:
                    self._p2 = max(0, min(255, pixel1 - new_d))
                else:
                    self._p2 = max(0, min(255, pixel1 + new_d))

                return bits_to_embed

        return 0

    def _get_modified_pair(self) -> Tuple[int, int]:
        """Get the modified pixel pair."""
        return int(self._p1), int(self._p2)

    def _extract_pair(self, pixel1: int, pixel2: int) -> List[int]:
        """Extract bits from a pixel pair."""
        d = abs(pixel1 - pixel2)

        # Find range for this difference
        for bits_count, (low, high) in enumerate(self.pvd_ranges):
            if low <= d <= high:
                # Extract based on range
                secret_value = d - low
                if bits_count == 0:
                    # 1 bit - ensure Python int
                    return [int(secret_value & 1)]
                else:
                    # 2 bits - ensure Python ints
                    return [int((secret_value >> i) & 1) for i in range(2)]

        return []
