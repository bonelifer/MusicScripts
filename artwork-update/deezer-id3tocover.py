#!/usr/bin/env python3
"""
Album Cover Updater

This script scans a music library directory for album folders, identifies missing or
low-resolution cover art, and replaces or adds high-resolution JPEG cover images
fetched from the Deezer API.

Key Features:
- Reads settings from `artwork-config.ini`
- Skips subfolders without valid MP3 files or metadata
- Respects existing high-resolution `cover.jpg` files
- Validates downloaded artwork for format, dimensions, and resolution
- Provides graceful shutdown on interrupt (Ctrl+C)

Configuration:
- [paths] rootmusicdir = /path/to/music
- [settings] MIN_RES = 500  (minimum acceptable resolution for artwork)

Usage:
    python3 cover_updater.py
    python3 cover_updater.py --debug   # Enables verbose debug logging

Log Output:
- Saves activity logs to `cover_updater.log`
"""

import os
import sys
import signal
import logging
import configparser
import requests
from PIL import Image, UnidentifiedImageError
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError, error as ID3Error
from pathlib import Path
from requests.exceptions import RequestException, Timeout
from io import BytesIO

# Constants
CONFIG_FILE = "artwork-config.ini"
LOG_FILE = "cover_updater.log"
DEEZER_API_URL = "https://api.deezer.com/search/album"
CD_PREFIXES = ('cd', 'disc', 'disk')  # Common disc subfolder prefixes
VALID_COVER_NAMES = ['cover.jpg']     # Recognized cover image filenames

# Global exit flag for safe shutdown
should_exit = False

def signal_handler(sig, frame):
    """
    Handle SIGINT (Ctrl+C) to allow graceful shutdown after processing the current album.
    """
    global should_exit
    logging.info("\n🛑 Received interrupt signal - finishing current album...")
    should_exit = True
    signal.signal(signal.SIGINT, original_sigint)  # Restore original handler

# Setup logging output to file and console
logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))

logger.addHandler(file_handler)
logger.addHandler(console_handler)

def load_config():
    """
    Load configuration from INI file and validate paths/settings.

    Returns:
        dict: Contains 'music_path' and 'min_res'

    Raises:
        FileNotFoundError: If the config file does not exist
        ValueError: If any setting is invalid
    """
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(f"Config file missing: {CONFIG_FILE}")
    
    config.read(CONFIG_FILE)
    try:
        settings = {
            'music_path': config.get("paths", "rootmusicdir"),
            'min_res': config.getint("settings", "MIN_RES")
        }

        # Verify music path exists
        if not os.path.isdir(settings['music_path']):
            raise ValueError(f"Invalid music path: {settings['music_path']}")
        
        return settings

    except Exception as e:
        logging.error(f"Config error: {str(e)}")
        raise

def is_cd_folder(name):
    """
    Determine if a folder name represents a CD subfolder.

    Args:
        name (str): Folder name

    Returns:
        bool: True if name matches known CD prefixes
    """
    return name.lower().startswith(CD_PREFIXES)

def get_artist_album_from_mp3(folder):
    """
    Extract artist and album metadata from the first MP3 found in the folder.

    Args:
        folder (str): Full path to album folder

    Returns:
        tuple: (artist, album) or (None, None)
    """
    for file in os.listdir(folder):
        if should_exit:
            return None, None

        if file.lower().endswith('.mp3'):
            try:
                tags = EasyID3(os.path.join(folder, file))
                artist = tags.get('artist', [''])[0].strip()
                album = tags.get('album', [''])[0].strip()
                if artist and album:
                    return artist, album
            except (ID3NoHeaderError, ID3Error):
                continue
    return None, None

def has_mp3s(folder):
    """
    Check if folder contains any MP3 files.

    Args:
        folder (str): Path to folder

    Returns:
        bool: True if MP3 files exist
    """
    try:
        return any(f.lower().endswith('.mp3') for f in os.listdir(folder))
    except PermissionError:
        logging.warning(f"Permission denied accessing {folder}")
        return False

def validate_image(image_data, min_res):
    """
    Verify image is a square JPEG and meets minimum resolution.

    Args:
        image_data (bytes): Raw image content
        min_res (int): Minimum resolution required (width and height)

    Returns:
        bool: True if image passes validation
    """
    try:
        with Image.open(BytesIO(image_data)) as img:
            if img.format not in ('JPEG', 'JFIF'):
                return False
            width, height = img.size
            return width >= min_res and height >= min_res and width == height
    except (UnidentifiedImageError, IOError, SyntaxError):
        return False

def get_existing_cover(folder, min_res):
    """
    Check for an existing high-quality cover.jpg file.

    Args:
        folder (str): Folder to check
        min_res (int): Minimum resolution

    Returns:
        str or None: Path to valid cover if found
    """
    for name in VALID_COVER_NAMES:
        path = os.path.join(folder, name)
        if os.path.exists(path):
            try:
                with Image.open(path) as img:
                    if (img.format in ('JPEG', 'JFIF') and 
                        img.width >= min_res and 
                        img.height >= min_res):
                        return path
            except (UnidentifiedImageError, IOError):
                continue
    return None

def has_any_cover(folder):
    """
    Check for the existence of any recognized cover file.

    Args:
        folder (str): Folder to check

    Returns:
        bool: True if any cover image exists
    """
    return any(os.path.exists(os.path.join(folder, name)) 
               for name in VALID_COVER_NAMES)

def fetch_deezer_artwork(artist, album):
    """
    Query Deezer API for high-res album artwork.

    Args:
        artist (str): Artist name
        album (str): Album title

    Returns:
        str or None: URL of the artwork
    """
    if should_exit:
        return None

    try:
        response = requests.get(
            DEEZER_API_URL,
            params={'q': f'artist:"{artist}" album:"{album}"', 'limit': 1},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        if data.get('data'):
            return data['data'][0].get('cover_xl') or data['data'][0].get('cover_big')
    except (RequestException, Timeout, ValueError) as e:
        logging.debug(f"API error for {artist} - {album}: {str(e)}")
        return None

def safe_save_image(image_url, save_path, min_res):
    """
    Download and safely save a validated image from a URL.

    Args:
        image_url (str): URL of the image
        save_path (str): Target file path
        min_res (int): Minimum resolution required

    Returns:
        bool: True on successful save and validation
    """
    if should_exit:
        return False

    temp_path = f"{save_path}.tmp"
    try:
        # Fetch image
        response = requests.get(image_url, stream=True, timeout=15)
        response.raise_for_status()

        # Write to temporary file
        with open(temp_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if should_exit:
                    raise KeyboardInterrupt()
                f.write(chunk)

        # Validate the image
        with open(temp_path, 'rb') as f:
            if not validate_image(f.read(), min_res):
                raise ValueError("Image failed validation")

        # Replace existing file if needed
        if os.path.exists(save_path):
            os.remove(save_path)
        os.rename(temp_path, save_path)
        return True

    except Exception as e:
        logging.warning(f"Download failed: {str(e)}")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return False

def process_folder(folder, root_path, min_res):
    """
    Process a folder to update or add album cover art.

    Args:
        folder (str): Folder path
        root_path (str): Base music library path
        min_res (int): Minimum resolution for artwork

    Returns:
        bool: True if artwork was updated
    """
    if should_exit:
        return False

    try:
        # Skip base folder or empty/non-music folders
        if Path(folder) == Path(root_path) or not has_mp3s(folder):
            return False

        # Read metadata
        artist, album = get_artist_album_from_mp3(folder)
        if not artist or not album:
            logging.debug(f"No metadata in {os.path.basename(folder)}")
            return False

        # Skip if cover is already valid
        existing_cover = get_existing_cover(folder, min_res)
        if existing_cover:
            logging.info(f"✓ {artist} - {album} (has good cover)")
            return False

        # Attempt to fetch and save new artwork
        artwork_url = fetch_deezer_artwork(artist, album)
        if not artwork_url:
            logging.debug(f"No artwork for {artist} - {album}")
            return False

        save_path = os.path.join(folder, 'cover.jpg')
        if safe_save_image(artwork_url, save_path, min_res):
            action = "upgraded" if has_any_cover(folder) else "added"
            logging.info(f"↑ {artist} - {album} ({action} cover)")
            return True

        return False

    except Exception as e:
        logging.error(f"! Error in {os.path.basename(folder)}: {str(e)}")
        return False

def main():
    """
    Main entry point: load config, process all album folders.
    """
    global original_sigint

    try:
        # Set interrupt handler
        original_sigint = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, signal_handler)

        # Read settings
        config = load_config()
        music_path = Path(config['music_path'])
        min_res = config['min_res']

        if not music_path.exists():
            raise FileNotFoundError(f"Music directory not found: {music_path}")

        logging.info(f"🚀 Starting Deezer cover art update (min {min_res}px)")
        logging.info(f"📁 Scanning: {music_path}")
        logging.info("Press Ctrl+C to stop after current album")

        # Walk through directories and process albums
        updated = 0
        for root, dirs, _ in os.walk(music_path):
            if should_exit:
                break

            if process_folder(root, music_path, min_res):
                updated += 1

            # Check for CD subfolders
            for dir_name in filter(is_cd_folder, dirs):
                if should_exit:
                    break

                cd_path = os.path.join(root, dir_name)
                if process_folder(cd_path, music_path, min_res):
                    updated += 1

        # Final log
        if should_exit:
            logging.info(f"🛑 Stopped early - updated {updated} covers")
        else:
            logging.info(f"✅ Completed! Updated {updated} covers")

        print(f"\nSummary:\n  - Albums processed: {music_path}")
        print(f"  - Covers updated: {updated}")
        print(f"  - Details in: {LOG_FILE}")

    except Exception as e:
        logging.critical(f"💥 Fatal error: {str(e)}")
        sys.exit(1)
    finally:
        signal.signal(signal.SIGINT, original_sigint)

if __name__ == '__main__':
    # Enable verbose debug logging with --debug flag
    if '--debug' in sys.argv:
        logging.getLogger().setLevel(logging.DEBUG)

    main()

