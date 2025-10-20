#!/usr/bin/env python
"""
Build script for Stegopy executable.
This script uses PyInstaller to create a standalone executable.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def clean_build_artifacts():
    """Remove previous build artifacts."""
    print("Cleaning previous build artifacts...")
    for folder in ['build', 'dist', '__pycache__']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"  Removed {folder}/")


def build_executable():
    """Build the executable using PyInstaller."""
    print("\nBuilding executable with PyInstaller...")
    
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--windowed',
        '--icon=stegopy/icon_embed.jpg',
        '--name=Stegopy',
        '--add-data=stegopy/ui/gui;stegopy/ui/gui',
        '--add-data=stegopy/config;stegopy/config',
        '--add-data=stegopy/icon_embed.jpg;.',
        '--hidden-import=PyQt6.QtCore',
        '--hidden-import=PyQt6.QtGui',
        '--hidden-import=PyQt6.QtWidgets',
        '--hidden-import=cryptography',
        '--hidden-import=cryptography.hazmat.primitives',
        '--hidden-import=cryptography.hazmat.primitives.ciphers',
        '--hidden-import=cryptography.hazmat.backends',
        '--hidden-import=PIL',
        '--hidden-import=numpy',
        '--hidden-import=scipy',
        '--hidden-import=pydantic',
        '--hidden-import=numba',
        '--exclude-module=matplotlib',
        '--exclude-module=pandas',
        '--distpath=dist',
        'stegopy/main.py'
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print("Build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        return False


def create_distribution_package():
    """Create a distributable package with the executable."""
    print("\nCreating distribution package...")
    
    dist_path = Path('dist')
    package_path = Path('stegopy_release')
    
    if package_path.exists():
        shutil.rmtree(package_path)
    
    package_path.mkdir()
    
    # Copy executable
    exe_name = 'Stegopy.exe' if sys.platform == 'win32' else 'Stegopy'
    exe_src = dist_path / exe_name
    exe_dst = package_path / exe_name
    
    if exe_src.exists():
        shutil.copy2(exe_src, exe_dst)
        print(f"  Copied {exe_name}")
    else:
        print(f"  Warning: {exe_name} not found")
    
    # Copy documentation
    for doc_file in ['README.txt', 'LICENSE']:
        if Path(doc_file).exists():
            shutil.copy2(doc_file, package_path / doc_file)
            print(f"  Copied {doc_file}")
    
    # Create a simple launch script for Windows
    if sys.platform == 'win32':
        batch_script = package_path / 'run_stegopy.bat'
        batch_script.write_text('@echo off\nSTART "" Stegopy.exe %*\n')
        print("  Created run_stegopy.bat launcher")
    
    print(f"\nDistribution package created in: {package_path.absolute()}")
    return package_path


def create_installer():
    """Create a more advanced installer (optional)."""
    print("\nNote: For advanced installer creation, consider using:")
    print("  - InnoSetup (Windows)")
    print("  - NSIS (Nullsoft Installer System)")
    print("  - PyInstaller's built-in onefile option is used above")


def main():
    """Main build process."""
    print("=" * 60)
    print("Stegopy Build Script")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('stegopy/main.py'):
        print("Error: stegopy/main.py not found. Are you in the right directory?")
        sys.exit(1)
    
    # Check dependencies
    print("\nChecking dependencies...")
    try:
        import PyInstaller
        print("  PyInstaller: OK")
    except ImportError:
        print("  Error: PyInstaller not installed")
        print("  Run: pip install pyinstaller")
        sys.exit(1)
    
    # Build process
    clean_build_artifacts()
    
    if not build_executable():
        sys.exit(1)
    
    package_path = create_distribution_package()
    create_installer()
    
    print("\n" + "=" * 60)
    print("Build Summary:")
    print(f"  Executable: dist/Stegopy.exe")
    print(f"  Package: {package_path}")
    print("=" * 60)
    print("\nTo share the application:")
    print(f"  1. Zip the '{package_path}' folder")
    print("  2. Distribute to users")
    print("  3. Users can extract and run 'Stegosuite.exe' directly")
    print("\nNo Python installation required for end users!")


if __name__ == '__main__':
    main()

