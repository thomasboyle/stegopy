"""
Configuration constants for Stegosuite.
"""

# Supported image formats
SUPPORTED_FORMATS = {
    "bmp": {"extension": ".bmp", "mime": "image/bmp"},
    "gif": {"extension": ".gif", "mime": "image/gif"},
    "jpg": {"extension": ".jpg", "mime": "image/jpeg"},
    "jpeg": {"extension": ".jpeg", "mime": "image/jpeg"},
    "png": {"extension": ".png", "mime": "image/png"},
}

# Payload structure constants
PAYLOAD_LENGTH_BYTES = 3  # 3 bytes = 16MB max payload
PAYLOAD_BYTE_ORDER = "big"  # Big endian for payload length

# Block types
BLOCK_TYPE_MESSAGE = 1
BLOCK_TYPE_FILE = 2

# Encryption settings
ENCRYPTION_ALGORITHM = "AES"
ENCRYPTION_MODE = "CBC"
KEY_DERIVATION_ITERATIONS = 100000

# Performance targets (in milliseconds)
PERFORMANCE_TARGETS = {
    "bmp": 250,
    "gif": 139,
    "jpg": 106,
    "jpeg": 106,
    "png": 66,
    "total": 5000,
}

# Default embedding method per format
DEFAULT_EMBEDDING_METHOD = {
    "bmp": "lsb",
    "gif": "lsb",
    "jpg": "lsb",
    "jpeg": "lsb",
    "png": "lsb",
}

# Point filter types
FILTER_NONE = 0
FILTER_HOMOGENEOUS = 1

# PVD embedding ranges
PVD_RANGES = [
    (0, 1),
    (2, 3),
    (4, 7),
    (8, 15),
    (16, 31),
    (32, 63),
    (64, 127),
    (128, 255),
]

# DCT block size (standard JPEG)
DCT_BLOCK_SIZE = 8
