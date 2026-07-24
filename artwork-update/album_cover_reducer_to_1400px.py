#!/usr/bin/env python3
"""
Ultimate Album Cover Resizer

Handles all special cases:
- Corrupted images
- Oversized images (decompression bombs)
- Various color modes (RGBA, P, etc.)
- Permission issues
- Non-image files
"""

import os
import sys
import logging
import configparser
from PIL import Image, ImageFile
import shutil

# Constants
CONFIG_FILE = "artwork-config.ini"
LOG_FILE = "cover_resizer.log"
MAX_RESOLUTION = 1400
RESIZE_QUALITY = 90
VALID_COVER_NAMES = ['cover.jpg']
MAX_PIXELS = 20000 * 20000  # 400MP limit for decompression bomb protection

# Configure Pillow to be more tolerant
ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = MAX_PIXELS

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))

logger.addHandler(file_handler)
logger.addHandler(console_handler)

def is_valid_image(filepath):
    """Check if file is a valid image with size constraints."""
    try:
        with Image.open(filepath) as img:
            img.verify()
            # Check reasonable dimensions
            if img.width * img.height > MAX_PIXELS:
                raise ValueError(f"Image too large: {img.width}x{img.height}")
        return True
    except Exception as e:
        logging.debug(f"Invalid image {filepath}: {str(e)}")
        return False

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

def resize_cover(cover_path):
    """Ultra-robust cover resizing with comprehensive error handling."""
    if not os.path.exists(cover_path):
        logging.debug(f"File not found: {cover_path}")
        return False

    if not os.access(cover_path, os.R_OK):
        logging.warning(f"Cannot read (permissions): {cover_path}")
        return False

    if not is_valid_image(cover_path):
        logging.warning(f"Invalid/corrupted/oversized image: {cover_path}")
        return False

    try:
        with Image.open(cover_path) as img:
            # Convert any image mode to RGB
            img = convert_to_rgb(img)
            
            # Check if resizing is needed
            if img.width <= MAX_RESOLUTION and img.height <= MAX_RESOLUTION:
                return False
            
            # Calculate new size maintaining aspect ratio
            ratio = min(MAX_RESOLUTION/img.width, MAX_RESOLUTION/img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            
            # Create temp file path
            temp_dir = os.path.dirname(cover_path)
            temp_name = f"resize_temp_{os.path.basename(cover_path)}"
            temp_path = os.path.join(temp_dir, temp_name)
            
            try:
                # Save with maximum quality settings
                img.resize(new_size, Image.LANCZOS).save(
                    temp_path,
                    format='JPEG',
                    quality=RESIZE_QUALITY,
                    optimize=True,
                    subsampling=0,
                    dpi=(300, 300)
                )
                
                # Verify the temp file before replacing original
                if not is_valid_image(temp_path):
                    raise ValueError("Temp file verification failed")
                
                # Create backup
                backup_path = f"{cover_path}.bak"
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                shutil.move(cover_path, backup_path)
                
                # Replace original
                shutil.move(temp_path, cover_path)
                
                logging.info(f"Resized {cover_path} from {img.width}x{img.height} to {new_size[0]}x{new_size[1]}")
                return True
                
            except Exception as save_error:
                logging.warning(f"Save failed for {cover_path}: {str(save_error)}")
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return False

    except Exception as e:
        logging.warning(f"Processing failed for {cover_path}: {str(e)}")
        return False

def main():
    """Main function with comprehensive progress tracking."""
    try:
        music_path = load_config()
        logging.info(f"Starting Album Cover Art Reducer resizing (max {MAX_RESOLUTION}px)")
        logging.info(f"Scanning: {music_path}")

        processed = 0
        resized = 0
        errors = 0
        skipped = 0

        for root, _, files in os.walk(music_path):
            for file in files:
                if file.lower() in VALID_COVER_NAMES:
                    processed += 1
                    cover_path = os.path.join(root, file)
                    result = resize_cover(cover_path)
                    if result is True:
                        resized += 1
                    elif result is False:
                        errors += 1
                    else:
                        skipped += 1

        logging.info(f"Completed! Processed: {processed}, Resized: {resized}, Errors: {errors}, Skipped: {skipped}")
        print(f"\nSummary Report:")
        print(f"  - Music library: {music_path}")
        print(f"  - Covers processed: {processed}")
        print(f"  - Covers resized: {resized}")
        print(f"  - Errors encountered: {errors}")
        print(f"  - Covers skipped (already correct size): {skipped}")
        print(f"  - Detailed log: {LOG_FILE}")

    except Exception as e:
        logging.critical(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    if '--debug' in sys.argv:
        logging.getLogger().setLevel(logging.DEBUG)
    main()
