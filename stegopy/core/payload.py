"""
Payload module for Stegosuite.

Handles serialization of data blocks (messages and files) for embedding.
"""

import os
from typing import List, Tuple, Optional

from stegopy.config.constants import (
    PAYLOAD_LENGTH_BYTES,
    BLOCK_TYPE_MESSAGE,
    BLOCK_TYPE_FILE,
)
from stegopy.util import byte_utils, crypto, compression


class Block:
    """Base class for payload blocks."""

    def __init__(self, block_type: int):
        self.block_type = block_type

    def serialize(self) -> bytes:
        """Serialize block to bytes."""
        raise NotImplementedError


class MessageBlock(Block):
    """A text message block."""

    def __init__(self, message: str):
        super().__init__(BLOCK_TYPE_MESSAGE)
        self.message = message

    def serialize(self) -> bytes:
        """Serialize message block: [type:1][length:4][data]"""
        message_bytes = self.message.encode("utf-8")
        length = len(message_bytes)
        return bytes([self.block_type]) + byte_utils.int_to_bytes(length, 4) + message_bytes

    @staticmethod
    def deserialize(data: bytes, offset: int) -> Tuple["MessageBlock", int]:
        """Deserialize message block from bytes."""
        length = byte_utils.bytes_to_int(data[offset : offset + 4])
        message_bytes = data[offset + 4 : offset + 4 + length]
        message = message_bytes.decode("utf-8")
        return MessageBlock(message), offset + 4 + length


class FileBlock(Block):
    """A file block."""

    def __init__(self, file_path: str):
        super().__init__(BLOCK_TYPE_FILE)
        self.file_path = file_path
        self.filename = os.path.basename(file_path)

    def serialize(self) -> bytes:
        """Serialize file block: [type:1][length:4][filename_len:2][filename][data]"""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File not found: {self.file_path}")

        with open(self.file_path, "rb") as f:
            file_data = f.read()

        filename_bytes = self.filename.encode("utf-8")
        filename_len = len(filename_bytes)
        file_len = len(file_data)

        return (
            bytes([self.block_type])
            + byte_utils.int_to_bytes(file_len, 4)
            + byte_utils.int_to_bytes(filename_len, 2)
            + filename_bytes
            + file_data
        )

    @staticmethod
    def deserialize(data: bytes, offset: int) -> Tuple["FileBlock", int]:
        """Deserialize file block from bytes."""
        file_len = byte_utils.bytes_to_int(data[offset : offset + 4])
        filename_len = byte_utils.bytes_to_int(data[offset + 4 : offset + 6], byte_order="big")
        filename_bytes = data[offset + 6 : offset + 6 + filename_len]
        filename = filename_bytes.decode("utf-8")
        file_data = data[offset + 6 + filename_len : offset + 6 + filename_len + file_len]

        # Create temporary FileBlock (we don't restore from extracted data the same way)
        block = FileBlock.__new__(FileBlock)
        block.block_type = BLOCK_TYPE_FILE
        block.file_path = filename
        block.filename = filename
        block._file_data = file_data
        return block, offset + 6 + filename_len + file_len


class Payload:
    """Container for all blocks to be embedded or extracted."""

    def __init__(self, password: str = ""):
        self.blocks: List[Block] = []
        self.password = password

    def add_message(self, message: str) -> None:
        """Add a message block to the payload."""
        self.blocks.append(MessageBlock(message))

    def add_file(self, file_path: str) -> None:
        """Add a file block to the payload."""
        self.blocks.append(FileBlock(file_path))

    def pack(self) -> bytes:
        """
        Pack all blocks into a continuous byte stream.

        Returns:
            Serialized payload (uncompressed and unencrypted)
        """
        packed = b"".join(block.serialize() for block in self.blocks)
        return packed

    def pack_and_prepare(self) -> bytes:
        """
        Pack, compress, and encrypt the payload for embedding.

        Returns:
            Ready-to-embed payload with header: [length:3][encrypted data]
        """
        packed = self.pack()

        # Compress
        compressed = compression.compress(packed)

        # Encrypt
        if self.password:
            encrypted = crypto.encrypt(compressed, self.password)
        else:
            encrypted = compressed

        # Prepare header with length
        payload_length = len(encrypted)
        length_bytes = byte_utils.int_to_bytes(payload_length, PAYLOAD_LENGTH_BYTES)

        return length_bytes + encrypted

    @staticmethod
    def unpack_and_extract(
        data: bytes, password: str = ""
    ) -> Tuple[List[Tuple[str, str]], bytes]:
        """
        Extract and unpack payload from embedded data.

        Args:
            data: Payload data (includes header with length)
            password: Password for decryption

        Returns:
            Tuple of (list of (block_type_str, content), raw_data)

        Raises:
            ValueError: If payload is corrupted or password is wrong
        """
        # Extract length
        if len(data) < PAYLOAD_LENGTH_BYTES:
            raise ValueError(
                f"Payload too short for header: got {len(data)} bytes, need {PAYLOAD_LENGTH_BYTES}. "
                "No valid embedded data found in image."
            )

        payload_length = byte_utils.bytes_to_int(data[:PAYLOAD_LENGTH_BYTES])
        
        # Validate payload length
        if payload_length == 0:
            raise ValueError(
                "Payload length is 0. Either no data was embedded, or the image is corrupted."
            )
        
        if payload_length > len(data) - PAYLOAD_LENGTH_BYTES:
            raise ValueError(
                f"Payload length ({payload_length}) exceeds available data "
                f"({len(data) - PAYLOAD_LENGTH_BYTES} bytes). "
                "Image may be corrupted or incomplete."
            )
        
        encrypted_data = data[PAYLOAD_LENGTH_BYTES : PAYLOAD_LENGTH_BYTES + payload_length]

        # Decrypt
        if password:
            try:
                decompressed_data = crypto.decrypt(encrypted_data, password)
            except ValueError as e:
                raise ValueError(f"Decryption failed (wrong password?): {str(e)}")
        else:
            decompressed_data = encrypted_data

        # Decompress
        try:
            packed_data = compression.decompress(decompressed_data)
        except ValueError as e:
            raise ValueError(
                f"Decompression failed: {str(e)}. "
                "The extracted data may be corrupted or incomplete."
            )

        # Unpack blocks
        blocks = []
        offset = 0
        while offset < len(packed_data):
            block_type = packed_data[offset]
            offset += 1

            if block_type == BLOCK_TYPE_MESSAGE:
                block, new_offset = MessageBlock.deserialize(packed_data, offset)
                blocks.append(("message", block.message))
                offset = new_offset
            elif block_type == BLOCK_TYPE_FILE:
                block, new_offset = FileBlock.deserialize(packed_data, offset)
                blocks.append(("file", (block.filename, block._file_data)))
                offset = new_offset
            else:
                raise ValueError(f"Unknown block type: {block_type}")

        return blocks, packed_data

    def get_capacity_estimate(self, image_format: str, embedding_method: str) -> int:
        """
        Estimate maximum payload capacity for an image.

        Args:
            image_format: Image format (bmp, gif, jpg, png)
            embedding_method: Embedding method (pvd, dct)

        Returns:
            Estimated capacity in bytes
        """
        # Placeholder - will be set by embedding method after analyzing image
        return 0
