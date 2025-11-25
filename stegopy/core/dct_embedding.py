"""
Enhanced DCT embedding for JPEG in Stegosuite.

Implements DCT-based embedding for JPEG format with compression-aware optimization.
Uses batch processing for significant performance improvements.
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
    """Enhanced DCT embedding for JPEG format with batch processing."""

    def __init__(self, image: ImageFormat, point_filter: PointFilter = None):
        """Initialize DCT embedding."""
        super().__init__(image, point_filter or NoFilter())
        if not isinstance(image, JPGImage):
            raise ValueError("DCT embedding only works with JPEG images")

    def _get_block_dimensions(self, height: int, width: int) -> Tuple[int, int, int, int]:
        """Calculate block grid dimensions and crop sizes."""
        h_blocks = max(0, (height - DCT_BLOCK_SIZE) // DCT_BLOCK_SIZE + 1)
        w_blocks = max(0, (width - DCT_BLOCK_SIZE) // DCT_BLOCK_SIZE + 1)
        crop_h = h_blocks * DCT_BLOCK_SIZE
        crop_w = w_blocks * DCT_BLOCK_SIZE
        return h_blocks, w_blocks, crop_h, crop_w

    def _image_to_blocks(self, channel: np.ndarray, h_blocks: int, w_blocks: int, 
                         crop_h: int, crop_w: int) -> np.ndarray:
        """Reshape image channel to array of 8x8 blocks for batch processing."""
        channel_crop = channel[:crop_h, :crop_w]
        blocks = channel_crop.reshape(h_blocks, DCT_BLOCK_SIZE, w_blocks, DCT_BLOCK_SIZE)
        blocks = blocks.transpose(0, 2, 1, 3).reshape(-1, DCT_BLOCK_SIZE, DCT_BLOCK_SIZE)
        return blocks

    def _blocks_to_image(self, blocks: np.ndarray, h_blocks: int, w_blocks: int,
                         crop_h: int, crop_w: int) -> np.ndarray:
        """Reshape array of 8x8 blocks back to image channel."""
        modified = blocks.reshape(h_blocks, w_blocks, DCT_BLOCK_SIZE, DCT_BLOCK_SIZE)
        modified = modified.transpose(0, 2, 1, 3).reshape(crop_h, crop_w)
        return modified

    def _batch_dct2d(self, blocks: np.ndarray) -> np.ndarray:
        """Apply 2D DCT to all blocks at once."""
        return fftpack.dct(fftpack.dct(blocks, axis=2, norm='ortho'), axis=1, norm='ortho')

    def _batch_idct2d(self, dct_blocks: np.ndarray) -> np.ndarray:
        """Apply 2D inverse DCT to all blocks at once."""
        return fftpack.idct(fftpack.idct(dct_blocks, axis=1, norm='ortho'), axis=2, norm='ortho')

    def embed(self, payload: Payload) -> ImageFormat:
        """
        Embed payload using batched DCT algorithm for better performance.

        Args:
            payload: Payload to embed

        Returns:
            Modified image with embedded payload

        Raises:
            ValueError: If payload is too large
        """
        payload_data = payload.pack_and_prepare()
        pixels = self.image.get_pixel_array().astype(np.float32)
        height, width = pixels.shape[:2]

        capacity = self.get_capacity()
        if len(payload_data) > capacity:
            raise ValueError(
                f"Payload too large: {len(payload_data)} bytes, but capacity is only {capacity} bytes"
            )

        # Extract working channel (red for RGB, full for grayscale)
        is_rgb = len(pixels.shape) == 3
        if is_rgb:
            channel = pixels[:, :, 0].copy()
        else:
            channel = pixels.copy()

        # Calculate block dimensions
        h_blocks, w_blocks, crop_h, crop_w = self._get_block_dimensions(height, width)
        total_blocks = h_blocks * w_blocks

        if total_blocks == 0:
            self.image.set_pixel_array(pixels.astype(np.uint8))
            return self.image

        # Reshape to blocks for batch processing
        blocks = self._image_to_blocks(channel, h_blocks, w_blocks, crop_h, crop_w)

        # Batch DCT on all blocks at once
        dct_blocks = self._batch_dct2d(blocks)

        # Convert payload to bits
        bit_data = list(byte_utils.iterate_bits(payload_data))
        num_bits = min(len(bit_data), total_blocks)

        # Embed bits in coefficient [1,1] of each block - vectorized where possible
        if num_bits > 0:
            bit_array = np.array(bit_data[:num_bits], dtype=np.float32)
            coeffs = dct_blocks[:num_bits, 1, 1]
            # Apply floor for bit=0, ceil for bit=1
            floored = np.floor(coeffs)
            ceiled = np.ceil(coeffs)
            dct_blocks[:num_bits, 1, 1] = np.where(bit_array == 0, floored, ceiled)

        self._report_progress(num_bits // 8, len(payload_data))

        # Batch IDCT on all blocks at once
        modified_blocks = self._batch_idct2d(dct_blocks)
        modified_blocks = np.clip(modified_blocks, 0, 255)

        # Reshape back to image
        modified_channel = self._blocks_to_image(modified_blocks, h_blocks, w_blocks, crop_h, crop_w)

        # Update pixels
        if is_rgb:
            pixels[:crop_h, :crop_w, 0] = modified_channel
        else:
            pixels[:crop_h, :crop_w] = modified_channel

        self.image.set_pixel_array(pixels.astype(np.uint8))
        return self.image

    def extract(self, password: str = "") -> Payload:
        """
        Extract payload from JPEG image using batched DCT.

        Args:
            password: Password for decryption

        Returns:
            Extracted payload

        Raises:
            ValueError: If extraction fails
        """
        pixels = self.image.get_pixel_array().astype(np.float32)
        height, width = pixels.shape[:2]

        # Extract working channel
        is_rgb = len(pixels.shape) == 3
        if is_rgb:
            channel = pixels[:, :, 0]
        else:
            channel = pixels

        # Calculate block dimensions
        h_blocks, w_blocks, crop_h, crop_w = self._get_block_dimensions(height, width)
        total_blocks = h_blocks * w_blocks

        if total_blocks == 0:
            raise ValueError("Image too small for DCT extraction")

        # Reshape to blocks for batch processing
        blocks = self._image_to_blocks(channel, h_blocks, w_blocks, crop_h, crop_w)

        # Batch DCT on all blocks at once
        dct_blocks = self._batch_dct2d(blocks)

        # Extract bits from coefficient [1,1] - fully vectorized
        coeffs = dct_blocks[:, 1, 1]
        fractional = coeffs - np.floor(coeffs)
        extracted_bits = (fractional >= 0.5).astype(np.uint8)

        # Convert bits to bytes using vectorized operation
        num_complete_bytes = len(extracted_bits) // 8
        if num_complete_bytes == 0:
            raise ValueError("Not enough blocks for extraction")

        # Reshape bits to bytes
        bit_matrix = extracted_bits[:num_complete_bytes * 8].reshape(-1, 8)
        powers = np.array([128, 64, 32, 16, 8, 4, 2, 1], dtype=np.uint8)
        extracted_data = np.sum(bit_matrix * powers, axis=1, dtype=np.uint8)

        # Unpack and extract payload
        blocks_result, _ = Payload.unpack_and_extract(bytes(extracted_data), password)

        # Create payload instance with extracted blocks
        payload = Payload(password)
        payload._extracted_blocks = blocks_result
        return payload

    def get_capacity(self) -> int:
        """Get maximum embedding capacity in bytes."""
        pixels = self.image.get_pixel_array()
        height, width = pixels.shape[:2]

        # Efficient calculation without creating lists
        h_blocks = max(0, (height - DCT_BLOCK_SIZE) // DCT_BLOCK_SIZE + 1)
        w_blocks = max(0, (width - DCT_BLOCK_SIZE) // DCT_BLOCK_SIZE + 1)
        total_blocks = h_blocks * w_blocks

        return total_blocks // 8
