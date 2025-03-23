#!/usr/bin/env python
"""
FRIDAY CLI Encryption Tool

This script is used to prepare the encrypted version of FRIDAY CLI for distribution.
It encrypts the core modules while preserving the import mechanism.
"""

import os
import sys
import argparse
from pathlib import Path
import dotenv

# Make sure we can import the FRIDAY code
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from friday.license.crypto import encrypt_directory


def encrypt_friday_core(src_dir: Path, verbose: bool = False) -> None:
    """Encrypt the core modules of FRIDAY CLI
    
    Args:
        src_dir: The source directory of the FRIDAY CLI package
        verbose: Whether to print verbose output
    """
    # Ensure the src_dir exists
    if not src_dir.exists() or not src_dir.is_dir():
        print(f"Error: {src_dir} is not a valid directory")
        sys.exit(1)
    
    # Find the core directory
    core_dir = src_dir / "friday" / "core"
    if not core_dir.exists() or not core_dir.is_dir():
        print(f"Error: Core directory not found at {core_dir}")
        sys.exit(1)
    
    print(f"\nEncrypting FRIDAY core modules in {core_dir}...")
    
    # Encrypt the core directory
    try:
        encrypted_count, skipped_count = encrypt_directory(core_dir)
        print(f"✅ Successfully encrypted {encrypted_count} files")
        if skipped_count > 0:
            print(f"ℹ️ Skipped {skipped_count} already encrypted files")
    except Exception as e:
        print(f"❌ Encryption failed: {str(e)}")
        sys.exit(1)


def main():
    # Load environment variables
    dotenv_path = Path(__file__).parent.parent.parent / ".env"
    if dotenv_path.exists():
        dotenv.load_dotenv(dotenv_path)
    
    parser = argparse.ArgumentParser(description="FRIDAY CLI Encryption Tool")
    parser.add_argument(
        "--src", 
        type=str, 
        default=str(Path(__file__).parent.parent.parent),
        help="Source directory of the FRIDAY CLI package"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    src_dir = Path(args.src)
    
    print("===== FRIDAY CLI Encryption Tool =====")
    encrypt_friday_core(src_dir, args.verbose)
    print("\n✨ Encryption completed successfully!")
    print("The package is now ready for distribution.")


if __name__ == "__main__":
    main()