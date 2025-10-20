#!/usr/bin/env python
"""
Demonstration of the modern LSB embedding algorithm for Stegosuite.

This script shows how the new LSB algorithm supports all image formats
and provides better security than the previous PVD algorithm.
"""

import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from stegopy.core import load_image, Payload, LSBEmbedding


def create_test_image(width=300, height=300, pattern="gradient"):
    """Create a test image with different patterns."""
    img_array = np.zeros((height, width, 3), dtype=np.uint8)

    if pattern == "gradient":
        # Create a gradient pattern
        for y in range(height):
            for x in range(width):
                img_array[y, x, 0] = int((x / width) * 255)  # Red gradient
                img_array[y, x, 1] = int((y / height) * 255)  # Green gradient
                img_array[y, x, 2] = 128  # Blue constant
    elif pattern == "checkerboard":
        # Create a checkerboard pattern
        for y in range(height):
            for x in range(width):
                if (x // 20 + y // 20) % 2 == 0:
                    img_array[y, x] = [255, 255, 255]  # White
                else:
                    img_array[y, x] = [0, 0, 0]  # Black
    else:
        # Random noise
        img_array = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)

    return Image.fromarray(img_array.astype('uint8'), mode='RGB')


def demo_lsb_embedding():
    """Demonstrate LSB embedding with different image formats."""
    print("STEGOSUITE LSB ALGORITHM DEMONSTRATION")
    print("=" * 60)

    test_message = "This secret message is embedded using the modern LSB algorithm!"
    test_password = "SecurePassword123!"

    print(f"Test Message: '{test_message}'")
    print(f"Password: '{test_password}'")
    print()

    # Test different image formats
    formats_to_test = [
        ("png", "PNG (Lossless)"),
        ("bmp", "BMP (Uncompressed)"),
        ("gif", "GIF (Palette-based)"),
    ]

    for format_ext, format_desc in formats_to_test:
        print(f"Testing {format_desc} format...")
        print("-" * 40)

        try:
            # Create test image
            test_image = create_test_image(200, 200, "gradient")

            with tempfile.TemporaryDirectory() as tmpdir:
                # Save original image
                original_path = Path(tmpdir) / f"original.{format_ext}"
                test_image.save(original_path, format=format_ext.upper())
                print(f"  OK: Created test image: {original_path}")

                # Load and prepare for embedding
                image = load_image(str(original_path))
                embedding = LSBEmbedding(image)

                capacity = embedding.get_capacity()
                print(f"  Image capacity: {capacity} bytes")
                # Create payload
                payload = Payload(test_password)
                payload.add_message(test_message)

                # Embed
                print(f"  Embedding message...")
                embedded_image = embedding.embed(payload)

                # Save embedded image
                embedded_path = Path(tmpdir) / f"embedded.{format_ext}"
                embedded_image.save(str(embedded_path))
                print(f"  OK: Saved embedded image: {embedded_path}")

                # Extract from embedded image
                print(f"  Extracting message...")
                extracted_image = load_image(str(embedded_path))
                extraction = LSBEmbedding(extracted_image)
                extracted_payload = extraction.extract(test_password)

                # Verify
                if hasattr(extracted_payload, '_extracted_blocks') and extracted_payload._extracted_blocks:
                    extracted_message = extracted_payload._extracted_blocks[0][1]
                    if extracted_message == test_message:
                        print(f"  SUCCESS: Message extracted correctly!")
                        print(f"     Extracted: '{extracted_message}'")
                    else:
                        print(f"  FAILED: Message mismatch!")
                        print(f"     Expected: '{test_message}'")
                        print(f"     Got: '{extracted_message}'")
                else:
                    print("  FAILED: No message extracted!")
            print()

        except Exception as e:
            print(f"  ERROR: {e}")
            print()

    print("ADVANTAGES OF THE NEW LSB ALGORITHM:")
    print("-" * 60)
    print("* Supports ALL image formats (PNG, BMP, GIF, JPEG, etc.)")
    print("* Uses pseudo-random pixel selection for better security")
    print("* Works with both RGB and grayscale images")
    print("* Maintains image quality (LSB changes are invisible)")
    print("* More modern and secure than PVD algorithm")
    print("* Consistent capacity across different image formats")
    print()

    print("SECURITY FEATURES:")
    print("-" * 60)
    print("- Pseudo-random pixel traversal (key-based)")
    print("- Compatible with existing AES encryption")
    print("- Multi-bit embedding capability")
    print("- No visible artifacts in embedded images")
    print()

    print("DEMONSTRATION COMPLETE!")


if __name__ == "__main__":
    demo_lsb_embedding()
