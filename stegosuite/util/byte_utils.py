"""
Byte manipulation utilities for Stegosuite.

Provides bit-level operations, byte serialization/deserialization, and bit iteration.
"""

from typing import Iterator, List


def int_to_bytes(value: int, length: int = 4, byte_order: str = "big") -> bytes:
    """
    Convert an integer to bytes.

    Args:
        value: Integer value to convert
        length: Number of bytes in result
        byte_order: "big" for big-endian, "little" for little-endian

    Returns:
        Bytes representation of the integer
    """
    return value.to_bytes(length, byteorder=byte_order)


def bytes_to_int(data: bytes, byte_order: str = "big") -> int:
    """
    Convert bytes to an integer.

    Args:
        data: Bytes to convert
        byte_order: "big" for big-endian, "little" for little-endian

    Returns:
        Integer value
    """
    return int.from_bytes(data, byteorder=byte_order)


def concat(*args: bytes) -> bytes:
    """
    Concatenate multiple byte sequences.

    Args:
        *args: Variable number of byte sequences

    Returns:
        Concatenated bytes
    """
    return b"".join(args)


def iterate_bits(data: bytes, byte_order: str = "big") -> Iterator[int]:
    """
    Iterate over individual bits in data.

    Args:
        data: Bytes to iterate
        byte_order: "big" for MSB first, "little" for LSB first

    Yields:
        Individual bits (0 or 1)
    """
    for byte in data:
        if byte_order == "big":
            # MSB first (big-endian bit order)
            for i in range(7, -1, -1):
                yield (byte >> i) & 1
        else:
            # LSB first (little-endian bit order)
            for i in range(8):
                yield (byte >> i) & 1


def bits_to_byte(bits: List[int], byte_order: str = "big") -> int:
    """
    Convert a list of bits to a byte.

    Args:
        bits: List of 8 bits (0 or 1)
        byte_order: "big" for MSB first, "little" for LSB first

    Returns:
        Byte value

    Raises:
        ValueError: If bits length is not 8
    """
    if len(bits) != 8:
        raise ValueError("bits must contain exactly 8 elements")

    byte = 0
    if byte_order == "big":
        for i, bit in enumerate(bits):
            byte |= (bit & 1) << (7 - i)
    else:
        for i, bit in enumerate(bits):
            byte |= (bit & 1) << i

    return byte


def set_bit(byte: int, index: int, value: int) -> int:
    """
    Set a specific bit in a byte.

    Args:
        byte: Original byte value
        index: Bit index (0-7, where 0 is LSB)
        value: Bit value (0 or 1)

    Returns:
        Modified byte value
    """
    if value:
        return byte | (1 << index)
    else:
        return byte & ~(1 << index)


def get_bit(byte: int, index: int) -> int:
    """
    Get a specific bit from a byte.

    Args:
        byte: Byte value
        index: Bit index (0-7, where 0 is LSB)

    Returns:
        Bit value (0 or 1)
    """
    return (byte >> index) & 1


def hamming_distance(byte1: int, byte2: int) -> int:
    """
    Calculate the Hamming distance (number of differing bits) between two bytes.

    Args:
        byte1: First byte
        byte2: Second byte

    Returns:
        Number of differing bits
    """
    xor = byte1 ^ byte2
    distance = 0
    while xor:
        distance += xor & 1
        xor >>= 1
    return distance
