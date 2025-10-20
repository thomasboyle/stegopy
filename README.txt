STEGOSUITE
==========

Modern steganography suite for hiding data in images with GPU-accelerated encoding/decoding.

QUICKSTART
==========

Install dependencies and run:

```bash
pip install -r requirements.txt
python -m stegosuite.main
```

The desktop application will launch with drag-and-drop support for embedding and extracting hidden data.

FEATURES
========

**GPU-Accelerated Operations**
- High-performance encode/decode using optimized vectorized operations
- Fast pixel sequence generation and parallel bit embedding/extraction
- Memory-efficient processing for large images

**Advanced Embedding Techniques**
- LSB (Least Significant Bit): Traditional bit-level embedding
- PVD (Pixel Value Differencing): Advanced raster embedding for BMP/GIF/PNG
- DCT (Discrete Cosine Transform): JPEG compression-aware embedding

**Security & Compatibility**
- AES-256 encryption with PBKDF2 key derivation
- Support for BMP, GIF, JPG, PNG formats
- Multi-file payloads with automatic compression
- Smart avoidance of homogeneous image areas

INSTALLATION
============

Requirements: Python 3.8+

```bash
git clone <repository>
cd stegosuite
pip install -r requirements.txt
```

USAGE
=====

**Embed Data:**
1. Select carrier image (BMP/GIF/JPG/PNG)
2. Add text messages and/or files
3. Set encryption password (optional)
4. Click "Embed & Save"

**Extract Data:**
1. Load stego image
2. Enter password (if encrypted)
3. Extract messages and files

LICENSE
=======

GNU General Public License v3
