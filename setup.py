"""Setup configuration for Stegosuite."""

from setuptools import setup, find_packages

with open("README.txt", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="stegosuite",
    version="0.9.0",
    author="Stegosuite Contributors",
    description="Modern Steganography Suite - Hide information in image files",
    long_description=long_description,
    long_description_content_type="text/plain",
    url="https://dev.stegosuite.org/stegosuite/stegosuite",
    license="GNU General Public License v3",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "Pillow>=12.0.0",
        "cryptography>=46.0.3",
        "PyQt6>=6.8.0",
        "pydantic>=2.12.3",
        "numpy>=2.3.4",
        "scipy>=1.16.2",
    ],
    extras_require={
        "dev": [
            "pytest>=8.4.2",
            "pytest-cov>=7.0.0",
            "black>=25.9.0",
            "ruff>=0.14.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "stegosuite=stegosuite.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security :: Cryptography",
    ],
)
