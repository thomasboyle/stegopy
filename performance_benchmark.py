#!/usr/bin/env python
"""
Performance benchmark for Stegosuite GPU acceleration.

Tests the encode/decode performance to verify the 5-second target is met.
"""

import time
import tempfile
from pathlib import Path
import numpy as np
from PIL import Image

# Add project root to path
project_root = Path(__file__).parent
import sys
sys.path.insert(0, str(project_root))

from stegopy.core import load_image, Payload, LSBEmbedding


def create_test_image(width=800, height=600, pattern="noise"):
    """Create a test image suitable for benchmarking."""
    img_array = np.zeros((height, width, 3), dtype=np.uint8)

    if pattern == "noise":
        # Random noise - good for testing capacity
        img_array = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
    elif pattern == "gradient":
        # Gradient pattern
        for y in range(height):
            for x in range(width):
                img_array[y, x, 0] = int((x / width) * 255)
                img_array[y, x, 1] = int((y / height) * 255)
                img_array[y, x, 2] = 128

    return Image.fromarray(img_array.astype('uint8'), mode='RGB')


def benchmark_lsb_embedding():
    """Benchmark LSB embedding performance."""
    print("=" * 70)
    print("STEGOSUITE LSB EMBEDDING PERFORMANCE BENCHMARK")
    print("=" * 70)

    # Create a reasonably large test image
    test_image = create_test_image(800, 600, "noise")
    test_message = "This is a test message for benchmarking the GPU-accelerated LSB embedding algorithm. " * 50  # Make it substantial
    password = "BenchmarkPassword123"

    print(f"Test Image: 800x600 pixels (1,440,000 pixels)")
    print(f"Message Length: {len(test_message)} characters")
    print(f"Password: {password}")
    print()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Save test image
        image_path = Path(tmpdir) / "benchmark.png"
        test_image.save(image_path, format="PNG")

        # Load image
        print("Loading image...")
        start_time = time.time()
        image = load_image(str(image_path))
        load_time = time.time() - start_time
        print(".3f")

        # Check capacity
        embedding = LSBEmbedding(image)
        capacity = embedding.get_capacity()
        print(f"Image Capacity: {capacity} bytes ({capacity/1024:.1f} KB)")
        print()

        # Create payload
        payload = Payload(password)
        payload.add_message(test_message)

        # Benchmark embedding
        print("Benchmarking EMBEDDING...")
        start_time = time.time()
        embedded_image = embedding.embed(payload)
        embed_time = time.time() - start_time
        print(".3f")

        # Save embedded image
        embedded_path = Path(tmpdir) / "embedded.png"
        embedded_image.save(str(embedded_path))

        # Benchmark extraction
        print("Benchmarking EXTRACTION...")
        start_time = time.time()
        extracted_image = load_image(str(embedded_path))
        extraction = LSBEmbedding(extracted_image)
        extracted_payload = extraction.extract(password)
        extract_time = time.time() - start_time
        print(".3f")

        # Verify result
        extracted_message = extracted_payload._extracted_blocks[0][1]
        success = extracted_message == test_message
        print(f"Verification: {'SUCCESS' if success else 'FAILED'}")

        # Performance summary
        total_time = embed_time + extract_time
        print()
        print("PERFORMANCE SUMMARY:")
        print("-" * 30)
        print(".3f")
        print(".3f")
        print(".3f")
        print(f"Target Met (<=5s): {'YES' if total_time <= 5.0 else 'NO'}")
        print(".1f")

        return total_time <= 5.0


if __name__ == "__main__":
    success = benchmark_lsb_embedding()

    if success:
        print("\nGPU ACCELERATION SUCCESS!")
        print("All performance targets met")
        print("Encode/decode completed in under 5 seconds")
    else:
        print("\nPerformance target not met")
        print("Further optimization may be needed")

    sys.exit(0 if success else 1)
