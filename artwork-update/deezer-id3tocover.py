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
- [settings] MIN_RES = 500  (fallback floor -- only relevant if nothing
  bigger is available; see TARGET_RES for the resolution this script
  actually aims for)

Usage:
    python3 deezer-id3tocover.py
    python3 deezer-id3tocover.py --debug             # Enables verbose debug logging
    python3 deezer-id3tocover.py -p /path/to/music    # Override rootmusicdir for this run

Log Output:
- Saves activity logs to `cover_updater.log`
"""

import os
import re
import sys
import signal
import logging
import argparse
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
# Deezer's API only documents cover_xl (~1000px), but its CDN quietly
# stores most covers up to 1400px and serves that actual image (never an
# error) when a larger size is requested in the URL than is available.
TARGET_RES = 1400

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
            'music_path': config.get("paths", "rootmusicdir", fallback=None),
            'min_res': config.getint("settings", "MIN_RES")
        }
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

def validate_image(image_data):
    """
    Verify image is a valid square JPEG.

    Resolution is intentionally not checked here: a download is never
    rejected outright for being small, since it may be the best a source
    can offer. See safe_save_image() for how MIN_RES factors into whether
    a downloaded candidate is worth keeping over an existing cover.

    Args:
        image_data (bytes): Raw image content

    Returns:
        bool: True if image passes validation
    """
    try:
        with Image.open(BytesIO(image_data)) as img:
            if img.format not in ('JPEG', 'JFIF'):
                return False
            width, height = img.size
            return width == height
    except (UnidentifiedImageError, IOError, SyntaxError):
        return False

def get_existing_cover(folder, target_res):
    """
    Check for an existing cover.jpg that already meets the target
    resolution, so it can be left alone instead of re-fetched.

    Args:
        folder (str): Folder to check
        target_res (int): Resolution a cover must meet to be left alone

    Returns:
        str or None: Path to a cover that already meets target_res
    """
    for name in VALID_COVER_NAMES:
        path = os.path.join(folder, name)
        if os.path.exists(path):
            try:
                with Image.open(path) as img:
                    if (img.format in ('JPEG', 'JFIF') and
                        img.width >= target_res and
                        img.height >= target_res):
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

def build_upsized_url(cover_url, target_res):
    """
    Rewrite a Deezer cover URL's size segment to request target_res.

    Args:
        cover_url (str): A cover_xl/cover_big URL, e.g. containing "1000x1000"
        target_res (int): Requested width/height in pixels

    Returns:
        str: The rewritten URL, or cover_url unchanged if no size segment
            was found to rewrite
    """
    return re.sub(r'\d+x\d+(?=[-.])', f'{target_res}x{target_res}', cover_url, count=1)

def fetch_deezer_artwork(artist, album):
    """
    Query Deezer API for album artwork, returning candidate URLs to try in
    priority order (largest requested size first).

    Args:
        artist (str): Artist name
        album (str): Album title

    Returns:
        list[str]: Candidate URLs, largest-first; empty if none found
    """
    if should_exit:
        return []

    try:
        response = requests.get(
            DEEZER_API_URL,
            params={'q': f'artist:"{artist}" album:"{album}"', 'limit': 1},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        if not data.get('data'):
            return []
        cover_url = data['data'][0].get('cover_xl') or data['data'][0].get('cover_big')
        if not cover_url:
            return []

        candidates = []
        upsized_url = build_upsized_url(cover_url, TARGET_RES)
        if upsized_url != cover_url:
            candidates.append(upsized_url)
        candidates.append(cover_url)
        return candidates
    except (RequestException, Timeout, ValueError) as e:
        logging.debug(f"API error for {artist} - {album}: {str(e)}")
        return []

def safe_save_image(candidates, save_path, min_res, existing_res=(0, 0)):
    """
    Try each candidate URL (largest first) and save the first one that
    downloads and validates.

    A candidate is never rejected purely for being smaller than min_res --
    it may be the best a source can offer. It IS rejected if it's smaller
    than the cover already on disk, unless that existing cover is itself
    below min_res (in which case any valid replacement is an improvement).

    Args:
        candidates (list[str]): Candidate image URLs, largest-first
        save_path (str): Target file path
        min_res (int): Floor below which an existing cover is always worth
            replacing, even by a same-or-smaller candidate
        existing_res (tuple[int, int]): Width/height of the current
            cover.jpg, or (0, 0) if there isn't one

    Returns:
        bool: True on successful save
    """
    if should_exit:
        return False

    temp_path = f"{save_path}.tmp"
    for image_url in candidates:
        if should_exit:
            return False
        try:
            response = requests.get(image_url, stream=True, timeout=15)
            response.raise_for_status()

            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if should_exit:
                        raise KeyboardInterrupt()
                    f.write(chunk)

            with open(temp_path, 'rb') as f:
                image_data = f.read()
            if not validate_image(image_data):
                raise ValueError("Image failed validation")

            with Image.open(BytesIO(image_data)) as img:
                new_res = img.size

            existing_pixels = existing_res[0] * existing_res[1]
            new_pixels = new_res[0] * new_res[1]
            existing_below_floor = existing_pixels and min(existing_res) < min_res
            if existing_pixels and new_pixels < existing_pixels and not existing_below_floor:
                logging.debug(
                    f"Candidate {new_res[0]}x{new_res[1]} is smaller than existing "
                    f"{existing_res[0]}x{existing_res[1]}; keeping existing cover"
                )
                os.remove(temp_path)
                return False

            if new_pixels < min_res * min_res:
                logging.info(
                    f"⚠ Best available is {new_res[0]}x{new_res[1]}, below the {min_res}px floor"
                )

            if os.path.exists(save_path):
                os.remove(save_path)
            os.rename(temp_path, save_path)
            return True

        except Exception as e:
            logging.debug(f"Candidate failed ({image_url}): {str(e)}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            continue

    logging.warning("All artwork candidates failed download or validation")
    return False

def process_folder(folder, root_path, min_res):
    """
    Process a folder to update or add album cover art.

    Args:
        folder (str): Folder path
        root_path (str or None): Base music library path (the walk's starting
            point, skipped so it isn't treated as an album itself). Pass
            None (as -i mode does) to process folder unconditionally.
        min_res (int): Minimum resolution for artwork

    Returns:
        bool: True if artwork was updated
    """
    if should_exit:
        return False

    try:
        # Skip base folder or empty/non-music folders
        if (root_path is not None and Path(folder) == Path(root_path)) or not has_mp3s(folder):
            return False

        # Read metadata
        artist, album = get_artist_album_from_mp3(folder)
        if not artist or not album:
            logging.debug(f"No metadata in {os.path.basename(folder)}")
            return False

        # Skip if cover already meets the target resolution
        existing_cover = get_existing_cover(folder, TARGET_RES)
        if existing_cover:
            logging.info(f"✓ {artist} - {album} (has good cover)")
            return False

        # Attempt to fetch a better candidate and compare against whatever exists
        candidates = fetch_deezer_artwork(artist, album)
        if not candidates:
            logging.debug(f"No artwork for {artist} - {album}")
            return False

        save_path = os.path.join(folder, 'cover.jpg')
        had_cover = has_any_cover(folder)
        existing_res = (0, 0)
        if had_cover:
            try:
                with Image.open(save_path) as img:
                    existing_res = img.size
            except (UnidentifiedImageError, IOError):
                pass

        if safe_save_image(candidates, save_path, min_res, existing_res):
            action = "upgraded" if had_cover else "added"
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

    parser = argparse.ArgumentParser(description="Update album artwork from Deezer.")
    parser.add_argument("-p", "--path", type=str, help="Override rootmusicdir from artwork-config.ini for this run.")
    parser.add_argument("-i", "--input", type=str, help="Process a specific folder (album or CD folder) instead of the whole library.")
    parser.add_argument("--debug", action="store_true", help="Enable debug-level logging.")
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Set interrupt handler
        original_sigint = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, signal_handler)

        # Read settings
        config = load_config()
        min_res = config['min_res']

        logging.info(f"🚀 Starting Deezer cover art update (target {TARGET_RES}px, floor {min_res}px)")

        updated = 0
        if args.input:
            if not os.path.isdir(args.input):
                logging.critical(f"💥 Fatal error: {args.input} is not a valid directory.")
                sys.exit(1)
            scanned = args.input
            if process_folder(args.input, None, min_res):
                updated += 1
        else:
            music_path_str = args.path or config['music_path']
            if not music_path_str:
                logging.critical("💥 Fatal error: no music directory set. Use -p <folder> or set [paths] rootmusicdir in artwork-config.ini.")
                sys.exit(1)
            music_path = Path(music_path_str)
            scanned = music_path

            if not music_path.exists():
                raise FileNotFoundError(f"Music directory not found: {music_path}")

            logging.info(f"📁 Scanning: {music_path}")
            logging.info("Press Ctrl+C to stop after current album")

            # Walk through directories and process albums
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

        print(f"\nSummary:\n  - Albums processed: {scanned}")
        print(f"  - Covers updated: {updated}")
        print(f"  - Details in: {LOG_FILE}")

    except Exception as e:
        logging.critical(f"💥 Fatal error: {str(e)}")
        sys.exit(1)
    finally:
        signal.signal(signal.SIGINT, original_sigint)

if __name__ == '__main__':
    main()

