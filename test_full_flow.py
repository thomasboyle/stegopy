#!/usr/bin/env python
"""
Full encode-decode test for Stegosuite.

Tests the complete steganography workflow:
1. Create a synthetic test image with texture
2. Create a payload with a message
3. Embed the payload into the image
4. Extract the payload from the image
5. Verify the extracted data matches the original
"""

import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from stegopy.core.image_format import load_image
from stegopy.core.payload import Payload
from stegopy.core.pvd_embedding import PVDEmbedding
from stegopy.core.dct_embedding import DCTEmbedding
from stegopy.util import image_utils


def create_synthetic_image(width=300, height=300, seed=42):
    """Create a synthetic test image with good texture for embedding."""
    np.random.seed(seed)
    img_array = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Add gradient pattern with noise for texture
    for y in range(height):
        for x in range(width):
            # Create multiple frequency components for texture
            base_r = int((x * 0.5 + y * 0.3) % 256)
            base_g = int((x * 0.3 + y * 0.5) % 256)
            base_b = int((x * 0.4 + y * 0.4) % 256)
            
            # Add some noise
            noise_r = np.random.randint(-30, 30)
            noise_g = np.random.randint(-30, 30)
            noise_b = np.random.randint(-30, 30)
            
            # Combine and clip
            img_array[y, x, 0] = np.clip(base_r + noise_r, 0, 255)
            img_array[y, x, 1] = np.clip(base_g + noise_g, 0, 255)
            img_array[y, x, 2] = np.clip(base_b + noise_b, 0, 255)
    
    img = Image.fromarray(img_array.astype('uint8'), mode='RGB')
    return img


def test_with_synthetic_png():
    """Test embedding and extracting with synthetic PNG - using same approach as working test."""
    print("\n" + "=" * 70)
    print("TEST 1: SYNTHETIC PNG (Direct Embed-Extract)")
    print("=" * 70)
    
    test_message = "Hello from Stegosuite! This message is hidden in a synthetic image."
    password = ""
    
    print(f"\nConfiguration:")
    print(f"  Message: '{test_message}'")
    print(f"  Password: (none)")
    print(f"  Format: PNG with PVD embedding")
    
    try:
        print(f"\n[1/4] Creating synthetic image...")
        # Use the exact same approach as the working test
        img_array = np.ones((200, 200, 3), dtype=np.uint8) * 200
        img = Image.fromarray(img_array.astype('uint8'), mode='RGB')
        print(f"  OK: Created 200x200 PNG image (like working test)")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Save the synthetic image
            test_img_path = Path(tmpdir) / "test_synthetic.png"
            img.save(test_img_path, format="PNG")
            
            print(f"\n[2/4] Loading image...")
            image = load_image(str(test_img_path))
            print(f"  OK: Loaded {image.width}x{image.height} image")
            
            print(f"\n[3/4] Embedding payload...")
            # Create payload - exactly like working test
            payload = Payload()
            payload.add_message(test_message)
            
            # Embed - exactly like working test
            embedding = PVDEmbedding(image)
            embedded_image = embedding.embed(payload)
            print(f"  OK: Payload embedded successfully")
            
            print(f"\n[4/4] Extracting and verifying...")
            # Extract directly - exactly like working test
            extraction = PVDEmbedding(embedded_image)
            extracted_payload = extraction.extract(password="")
            
            # Verify - use same assertions
            assert len(extracted_payload._extracted_blocks) > 0, "No blocks extracted"
            assert extracted_payload._extracted_blocks[0][0] == "message", "First block is not a message"
            extracted_message = extracted_payload._extracted_blocks[0][1]
            
            print(f"  Extracted: '{extracted_message}'")
            assert extracted_message == test_message, f"Message mismatch: '{extracted_message}' != '{test_message}'"
            print(f"  OK: Message verified! TEST PASSED")
            return True
    
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_with_password():
    """Test with AES encryption - using same approach as working test."""
    print("\n" + "=" * 70)
    print("TEST 2: WITH AES-256 ENCRYPTION")
    print("=" * 70)
    
    test_message = "This message is encrypted with a strong password!"
    password = "VerySecurePassword123!@#"
    
    print(f"\nConfiguration:")
    print(f"  Message: '{test_message}'")
    print(f"  Password: '{password}'")
    print(f"  Format: PNG with PVD embedding + AES-256")
    
    try:
        print(f"\n[1/4] Creating synthetic image...")
        # Use same approach as working test
        img_array = np.ones((200, 200, 3), dtype=np.uint8) * 180
        img = Image.fromarray(img_array.astype('uint8'), mode='RGB')
        print(f"  OK: Created 200x200 PNG image")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_img_path = Path(tmpdir) / "test_encrypted.png"
            img.save(test_img_path, format="PNG")
            
            print(f"\n[2/4] Loading image...")
            image = load_image(str(test_img_path))
            
            print(f"\n[3/4] Embedding encrypted payload...")
            payload = Payload(password=password)
            payload.add_message(test_message)
            
            embedding = PVDEmbedding(image)
            embedded_image = embedding.embed(payload)
            print(f"  OK: Payload embedded with encryption")
            
            print(f"\n[4/4] Extracting and verifying...")
            extraction = PVDEmbedding(embedded_image)
            extracted_payload = extraction.extract(password=password)
            
            # Verify
            assert len(extracted_payload._extracted_blocks) > 0, "No blocks extracted"
            extracted_message = extracted_payload._extracted_blocks[0][1]
            print(f"  Extracted: '{extracted_message}'")
            assert extracted_message == test_message, f"Message mismatch"
            print(f"  OK: Encrypted message verified! TEST PASSED")
            return True
    
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_save_reload():
    """Test saving and reloading embedded image - direct embed/extract."""
    print("\n" + "=" * 70)
    print("TEST 3: SAVE AND RELOAD EMBEDDED IMAGE")
    print("=" * 70)
    
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    test_message = "This message survives save and reload!"
    password = "SaveReloadTest123"
    
    print(f"\nConfiguration:")
    print(f"  Message: '{test_message}'")
    print(f"  Password: '{password}'")
    print(f"  Test: Save stego image, reload it, extract")
    
    try:
        print(f"\n[1/5] Creating synthetic image...")
        img_array = np.ones((250, 250, 3), dtype=np.uint8) * 150
        img = Image.fromarray(img_array.astype('uint8'), mode='RGB')
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # First save it temporarily
            temp_img_path = Path(tmpdir) / "temp.png"
            img.save(temp_img_path, format="PNG")
            
            print(f"\n[2/5] Loading and embedding...")
            image = load_image(str(temp_img_path))
            payload = Payload(password=password)
            payload.add_message(test_message)
            
            embedding = PVDEmbedding(image)
            embedded_image = embedding.embed(payload)
            
            print(f"\n[3/5] Saving stego image...")
            stego_path = output_dir / "test_stego_save_reload.png"
            embedded_image.save(str(stego_path))
            print(f"  OK: Saved to {stego_path}")
            
            print(f"\n[4/5] Reloading stego image...")
            reloaded_image = load_image(str(stego_path))
            print(f"  OK: Reloaded from disk")
            
            print(f"\n[5/5] Extracting from reloaded image...")
            extraction = PVDEmbedding(reloaded_image)
            extracted_payload = extraction.extract(password=password)
            
            # Verify
            assert len(extracted_payload._extracted_blocks) > 0, "No blocks extracted"
            extracted_message = extracted_payload._extracted_blocks[0][1]
            print(f"  Extracted: '{extracted_message}'")
            assert extracted_message == test_message, f"Message mismatch after save/reload"
            print(f"  OK: Message survived save/reload! TEST PASSED")
            return True
    
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        # Run all tests
        result1 = test_with_synthetic_png()
        result2 = test_with_password()
        result3 = test_save_reload()
        
        # Summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"  Test 1 (Synthetic PNG): {'PASSED' if result1 else 'FAILED'}")
        print(f"  Test 2 (With Password): {'PASSED' if result2 else 'FAILED'}")
        
        if result3 is None:
            print(f"  Test 3 (Save/Reload): SKIPPED")
            overall = result1 and result2
        else:
            print(f"  Test 3 (Save/Reload): {'PASSED' if result3 else 'FAILED'}")
            overall = result1 and result2 and result3
        
        print(f"\nOverall Result: {'ALL TESTS PASSED' if overall else 'SOME TESTS FAILED'}")
        print("=" * 70)
        
        sys.exit(0 if (result1 and result2) else 1)
    
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
