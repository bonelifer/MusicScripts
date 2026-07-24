#!/usr/bin/env python3
"""
Cover Image Reducer

Reduces quality of cover.jpg (when original is 1.0 MiB or larger) and replaces it
using configuration from artwork-config.ini
"""

import os
import sys
import logging
import tempfile
import configparser
from PIL import Image, ImageFile

# Constants
CONFIG_FILE = "artwork-config.ini"
LOG_FILE = "cover_reducer.log"
REDUCE_QUALITY = 90
MIN_SIZE_TO_REDUCE = 1 * 1024 * 1024  # 1.0 MiB
VALID_COVER_NAMES = ['cover.jpg']

# Configure Pillow to be more tolerant
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))

logger.addHandler(file_handler)
logger.addHandler(console_handler)

def load_config():
    """Load and validate configuration."""
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(f"Config file missing: {CONFIG_FILE}")
    
    config.read(CONFIG_FILE)
    try:
        music_path = config.get("paths", "rootmusicdir")
        if not os.path.isdir(music_path):
            raise ValueError(f"Invalid music path: {music_path}")
        return music_path
    except Exception as e:
        logging.error(f"Config error: {str(e)}")
        raise

def convert_to_rgb(img):
    """Convert any image mode to RGB."""
    if img.mode == 'RGB':
        return img
    if img.mode == 'RGBA':
        return img.convert('RGB')
    if img.mode == 'P':
        return img.convert('RGB')
    if img.mode == 'L':
        return img.convert('RGB')
    return img.convert('RGB')

def reduce_cover(cover_path):
    """Reduce cover image quality if it meets size requirements and replace original."""
    if not os.path.exists(cover_path):
        logging.debug(f"File not found: {cover_path}")
        return False

    # Check file size
    file_size = os.path.getsize(cover_path)
    if file_size < MIN_SIZE_TO_REDUCE:
        logging.debug(f"File too small to reduce: {cover_path} ({file_size/1024/1024:.2f} MiB)")
        return False

    try:
        # Create temporary file
        temp_fd, temp_path = tempfile.mkstemp(suffix='.jpg', dir=os.path.dirname(cover_path))
        os.close(temp_fd)  # Close the file descriptor as PIL will open the file
        
        with Image.open(cover_path) as img:
            # Convert any image mode to RGB
            img = convert_to_rgb(img)
            
            # Save with reduced quality to temp file
            img.save(
                temp_path,
                format='JPEG',
                quality=REDUCE_QUALITY,
                optimize=True
            )
            
            # Verify the temp file
            try:
                with Image.open(temp_path) as test_img:
                    test_img.verify()
            except Exception as verify_error:
                logging.warning(f"Temp file verification failed: {str(verify_error)}")
                os.remove(temp_path)
                return False
            
            # Create backup (optional)
            backup_path = f"{cover_path}.bak"
            if os.path.exists(backup_path):
                os.remove(backup_path)
            os.rename(cover_path, backup_path)
            
            # Replace original
            os.rename(temp_path, cover_path)
            
            # Verify the new file size
            new_size = os.path.getsize(cover_path)
            logging.info(f"Reduced {cover_path} from {file_size/1024/1024:.2f} MiB to {new_size/1024/1024:.2f} MiB")
            return True

    except Exception as e:
        logging.warning(f"Processing failed for {cover_path}: {str(e)}")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return False

def main():
    """Main function to process all cover images."""
    try:
        music_path = load_config()
        logging.info(f"Starting Album Cover Compressor resolution reduction (quality {REDUCE_QUALITY})")
        logging.info(f"Scanning: {music_path}")

        processed = 0
        reduced = 0
        errors = 0
        skipped = 0

        for root, _, files in os.walk(music_path):
            for file in files:
                if file.lower() in VALID_COVER_NAMES:
                    processed += 1
                    cover_path = os.path.join(root, file)
                    result = reduce_cover(cover_path)
                    if result is True:
                        reduced += 1
                    elif result is False:
                        skipped += 1
                    else:
                        errors += 1

        logging.info(f"Completed! Processed: {processed}, Reduced: {reduced}, Errors: {errors}, Skipped: {skipped}")
        print(f"\nSummary Report:")
        print(f"  - Music library: {music_path}")
        print(f"  - Covers processed: {processed}")
        print(f"  - Covers reduced: {reduced}")
        print(f"  - Errors encountered: {errors}")
        print(f"  - Covers skipped: {skipped}")
        print(f"  - Detailed log: {LOG_FILE}")

    except Exception as e:
        logging.critical(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    if '--debug' in sys.argv:
        logging.getLogger().setLevel(logging.DEBUG)
    main()
