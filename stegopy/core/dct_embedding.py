"""
Enhanced DCT embedding for JPEG in Stegosuite.

Implements DCT-based embedding for JPEG format with compression-aware optimization.
"""

import numpy as np
from typing import List, Tuple
from scipy import fftpack

from stegopy.core.embedding import EmbeddingMethod
from stegopy.core.payload import Payload
from stegopy.core.image_format import ImageFormat, JPGImage
from stegopy.core.point_filter import PointFilter, NoFilter
from stegopy.util import byte_utils
from stegopy.config.constants import DCT_BLOCK_SIZE


class DCTEmbedding(EmbeddingMethod):
    """Enhanced DCT embedding for JPEG format."""

    def __init__(self, image: ImageFormat, point_filter: PointFilter = None):
        """Initialize DCT embedding."""
        super().__init__(image, point_filter or NoFilter())
        if not isinstance(image, JPGImage):
            raise ValueError("DCT embedding only works with JPEG images")

    def embed(self, payload: Payload) -> ImageFormat:
        """
        Embed payload using DCT algorithm.

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
        pixels = self.image.get_pixel_array().astype(np.float32)
        height, width = pixels.shape[:2]

        # Check capacity
        capacity = self.get_capacity()
        if len(payload_data) > capacity:
            raise ValueError(
                f"Payload too large: {len(payload_data)} bytes, but capacity is only {capacity} bytes"
            )

        # Process image in 8x8 blocks
        embedded_pixels = pixels.copy()
        bit_stream = byte_utils.iterate_bits(payload_data)
        embedded_count = 0

        for y in range(0, height - DCT_BLOCK_SIZE, DCT_BLOCK_SIZE):
            for x in range(0, width - DCT_BLOCK_SIZE, DCT_BLOCK_SIZE):
                # Extract block
                block = pixels[y : y + DCT_BLOCK_SIZE, x : x + DCT_BLOCK_SIZE]

                # For RGB images, use only the first (red) channel
                if len(block.shape) == 3:
                    channel_block = block[:, :, 0]
                else:
                    channel_block = block

                # Embed in this block
                modified_block, bits_embedded = self._embed_in_block(channel_block, bit_stream)

                # Update embedded image
                if len(block.shape) == 3:
                    embedded_pixels[y : y + DCT_BLOCK_SIZE, x : x + DCT_BLOCK_SIZE, 0] = modified_block
                else:
                    embedded_pixels[y : y + DCT_BLOCK_SIZE, x : x + DCT_BLOCK_SIZE] = modified_block
                embedded_count += bits_embedded

                # Report progress
                if embedded_count % 1000 == 0:
                    self._report_progress(embedded_count // 8, len(payload_data))

        # Update image with embedded pixels
        self.image.set_pixel_array(embedded_pixels.astype(np.uint8))
        return self.image

    def extract(self, password: str = "") -> Payload:
        """
        Extract payload from JPEG image using DCT.

        Args:
            password: Password for decryption

        Returns:
            Extracted payload

        Raises:
            ValueError: If extraction fails
        """
        pixels = self.image.get_pixel_array().astype(np.float32)
        height, width = pixels.shape[:2]

        # Extract bits from blocks
        extracted_bits = []

        for y in range(0, height - DCT_BLOCK_SIZE, DCT_BLOCK_SIZE):
            for x in range(0, width - DCT_BLOCK_SIZE, DCT_BLOCK_SIZE):
                # Extract block
                block = pixels[y : y + DCT_BLOCK_SIZE, x : x + DCT_BLOCK_SIZE]

                # For RGB images, use only the first (red) channel
                if len(block.shape) == 3:
                    channel_block = block[:, :, 0]
                else:
                    channel_block = block

                # Extract bits from this block
                bits = self._extract_from_block(channel_block)
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
        payload._extracted_blocks = blocks
        return payload

    def get_capacity(self) -> int:
        """Get maximum embedding capacity in bytes."""
        pixels = self.image.get_pixel_array()
        height, width = pixels.shape[:2]

        # Calculate exact number of blocks that will be processed (matches embedding/extraction loops)
        blocks_horizontal = len(list(range(0, width - DCT_BLOCK_SIZE, DCT_BLOCK_SIZE)))
        blocks_vertical = len(list(range(0, height - DCT_BLOCK_SIZE, DCT_BLOCK_SIZE)))
        total_blocks = blocks_horizontal * blocks_vertical

        # Each block contributes 1 bit, so capacity in bytes is total_blocks // 8
        capacity = total_blocks // 8

        return capacity

    def _embed_in_block(self, block: np.ndarray, bit_stream) -> Tuple[np.ndarray, int]:
        """
        Embed bits in an 8x8 DCT block.

        Args:
            block: 8x8 pixel block (single channel)
            bit_stream: Iterator of bits to embed

        Returns:
            Tuple of (modified_block, bits_embedded)
        """
        # Apply DCT
        dct_block = fftpack.dct(fftpack.dct(block.T, axis=0, norm="ortho").T, axis=1, norm="ortho")

        # Try to embed 1 bit in the DC component and mid-frequency components
        try:
            bit = next(bit_stream)
            # Modify DC component based on bit
            if bit == 0:
                dct_block[1, 1] = np.floor(dct_block[1, 1])
            else:
                dct_block[1, 1] = np.ceil(dct_block[1, 1])
            bits_embedded = 1
        except StopIteration:
            bits_embedded = 0

        # Apply inverse DCT
        modified_block = fftpack.idct(fftpack.idct(dct_block, axis=0, norm="ortho").T, axis=1, norm="ortho").T

        # Clip values to valid range
        modified_block = np.clip(modified_block, 0, 255)

        return modified_block, bits_embedded

    def _extract_from_block(self, block: np.ndarray) -> List[int]:
        """
        Extract bits from an 8x8 DCT block.

        Args:
            block: 8x8 pixel block (single channel)

        Returns:
            List of extracted bits
        """
        # Apply DCT
        dct_block = fftpack.dct(fftpack.dct(block.T, axis=0, norm="ortho").T, axis=1, norm="ortho")

        # Extract bit from DC component
        dc_value = dct_block[1, 1]
        # Ensure we return Python int, not NumPy type
        bit = int(1 if float(dc_value - np.floor(dc_value)) >= 0.5 else 0)

        return [bit]
