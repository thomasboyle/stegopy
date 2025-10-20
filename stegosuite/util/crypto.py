"""
Cryptography utilities for Stegosuite.

Handles AES encryption/decryption of payload data using password-based key derivation.
"""

import os
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

from stegosuite.config.constants import (
    ENCRYPTION_ALGORITHM,
    KEY_DERIVATION_ITERATIONS,
)


def derive_key(password: str, salt: bytes, key_length: int = 32) -> bytes:
    """
    Derive an encryption key from a password using PBKDF2.

    Args:
        password: User-provided password string
        salt: Salt bytes for key derivation
        key_length: Length of derived key in bytes (default 32 for AES-256)

    Returns:
        Derived key bytes
    """
    password_bytes = password.encode("utf-8")
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=key_length,
        salt=salt,
        iterations=KEY_DERIVATION_ITERATIONS,
    )
    return kdf.derive(password_bytes)


def encrypt(data: bytes, password: str) -> bytes:
    """
    Encrypt data using AES-256-CBC with password-based key derivation.

    Args:
        data: Data to encrypt
        password: Password for key derivation

    Returns:
        Encrypted data (IV + ciphertext)

    Raises:
        ValueError: If encryption fails
    """
    if not password:
        password = ""

    try:
        # Generate random IV and salt
        iv = os.urandom(16)
        salt = os.urandom(16)

        # Derive key from password
        key = derive_key(password, salt)

        # Encrypt data
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
        )
        encryptor = cipher.encryptor()

        # Add PKCS7 padding
        plaintext = _add_pkcs7_padding(data)
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()

        # Return salt + IV + ciphertext
        return salt + iv + ciphertext

    except Exception as e:
        raise ValueError(f"Encryption failed: {str(e)}")


def decrypt(encrypted_data: bytes, password: str) -> bytes:
    """
    Decrypt data encrypted with the encrypt function.

    Args:
        encrypted_data: Encrypted data (salt + IV + ciphertext)
        password: Password for key derivation

    Returns:
        Decrypted data

    Raises:
        ValueError: If decryption fails
    """
    if not password:
        password = ""

    try:
        # Extract salt, IV, and ciphertext
        salt = encrypted_data[:16]
        iv = encrypted_data[16:32]
        ciphertext = encrypted_data[32:]

        # Derive key from password
        key = derive_key(password, salt)

        # Decrypt data
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
        )
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        # Remove PKCS7 padding
        return _remove_pkcs7_padding(plaintext)

    except Exception as e:
        raise ValueError(f"Decryption failed: {str(e)}")


def _add_pkcs7_padding(data: bytes, block_size: int = 16) -> bytes:
    """Add PKCS7 padding to data."""
    padding_length = block_size - (len(data) % block_size)
    padding = bytes([padding_length] * padding_length)
    return data + padding


def _remove_pkcs7_padding(data: bytes) -> bytes:
    """Remove PKCS7 padding from data."""
    padding_length = data[-1]
    if padding_length > 16 or padding_length == 0:
        raise ValueError("Invalid padding")
    return data[:-padding_length]
