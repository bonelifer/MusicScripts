#!/usr/bin/env python3
"""
Last.fm Cover Art Updater

This script scans a music library directory for album folders and adds cover art
fetched from Last.fm when missing.

Key Features:
- Reads settings from `artwork-config.ini`
- Skips subfolders without valid MP3 files or metadata
- Respects existing cover.jpg files
- Provides graceful shutdown on interrupt (Ctrl+C)

Configuration:
- [paths] rootmusicdir = /path/to/music
- [lastfm] API_KEY = your_lastfm_api_key

Usage:
    python3 lastfm-id3tocover.py
"""

import os
import sys
import signal
import logging
import configparser
import requests
from mutagen.id3 import ID3, error as ID3Error
from pathlib import Path
from requests.exceptions import RequestException, Timeout

# Constants
CONFIG_FILE = "artwork-config.ini"
LOG_FILE = "lastfm_cover_updater.log"
VALID_COVER_NAMES = ['cover.jpg']  # Recognized cover image filenames

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
        dict: Contains 'music_path' and 'api_key'

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
            'api_key': config.get("lastfm", "API_KEY")
        }

        # Verify music path exists
        if not os.path.isdir(settings['music_path']):
            raise ValueError(f"Invalid music path: {settings['music_path']}")
        
        return settings

    except Exception as e:
        logging.error(f"Config error: {str(e)}")
        raise

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

def get_artist_album_from_id3(mp3_path):
    """
    Extracts the artist and album from the ID3 tags of an MP3 file.

    Returns:
        tuple: (artist, album) or (None, None)
    """
    try:
        audio = ID3(mp3_path)
        artist = audio.get('TPE1', None)
        album = audio.get('TALB', None)
        return artist.text[0] if artist else None, album.text[0] if album else None
    except ID3Error as e:
        logging.error(f"Error reading ID3 tags for {mp3_path}: {e}")
        return None, None

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

def fetch_lastfm_artwork(artist, album, api_key):
    """
    Query Last.fm API for album artwork.

    Args:
        artist (str): Artist name
        album (str): Album title
        api_key (str): Last.fm API key

    Returns:
        str or None: URL of the artwork
    """
    if should_exit:
        return None

    try:
        url = f"http://ws.audioscrobbler.com/2.0/?method=album.getinfo&api_key={api_key}&artist={artist}&album={album}&format=json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data['album']['image'][3]['#text']  # 3 is the large image size
    except (RequestException, Timeout, KeyError, ValueError) as e:
        logging.debug(f"API error for {artist} - {album}: {str(e)}")
        return None

def safe_save_image(image_url, save_path):
    """
    Download and save an image from a URL.

    Args:
        image_url (str): URL of the image
        save_path (str): Target file path

    Returns:
        bool: True on successful save
    """
    if should_exit:
        return False

    temp_path = f"{save_path}.tmp"
    try:
        response = requests.get(image_url, stream=True, timeout=15)
        response.raise_for_status()

        with open(temp_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if should_exit:
                    raise KeyboardInterrupt()
                f.write(chunk)

        if os.path.exists(save_path):
            os.remove(save_path)
        os.rename(temp_path, save_path)
        return True

    except Exception as e:
        logging.warning(f"Download failed: {str(e)}")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return False

def process_folder(folder, root_path, api_key):
    """
    Process a folder to add missing album cover art.

    Args:
        folder (str): Folder path
        root_path (str): Base music library path
        api_key (str): Last.fm API key

    Returns:
        bool: True if artwork was added
    """
    if should_exit:
        return False

    try:
        # Skip base folder or empty/non-music folders
        if Path(folder) == Path(root_path) or not has_mp3s(folder):
            return False

        # Find first MP3 to get metadata
        mp3_files = [f for f in os.listdir(folder) if f.lower().endswith('.mp3')]
        if not mp3_files:
            return False

        first_mp3 = os.path.join(folder, mp3_files[0])
        artist, album = get_artist_album_from_id3(first_mp3)
        if not artist or not album:
            logging.debug(f"No metadata in {os.path.basename(folder)}")
            return False

        # Skip if cover already exists
        if has_any_cover(folder):
            logging.info(f"✓ {artist} - {album} (has cover)")
            return False

        # Attempt to fetch and save new artwork
        artwork_url = fetch_lastfm_artwork(artist, album, api_key)
        if not artwork_url:
            logging.debug(f"No artwork for {artist} - {album}")
            return False

        save_path = os.path.join(folder, 'cover.jpg')
        if safe_save_image(artwork_url, save_path):
            logging.info(f"↑ {artist} - {album} (added cover)")
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
        api_key = config['api_key']

        if not music_path.exists():
            raise FileNotFoundError(f"Music directory not found: {music_path}")

        logging.info(f"🚀 Starting Last.fm cover art update")
        logging.info(f"📁 Scanning: {music_path}")
        logging.info("Press Ctrl+C to stop after current album")

        # Walk through directories and process albums
        updated = 0
        for root, dirs, _ in os.walk(music_path):
            if should_exit:
                break

            if process_folder(root, music_path, api_key):
                updated += 1

        # Final log
        if should_exit:
            logging.info(f"🛑 Stopped early - added {updated} covers")
        else:
            logging.info(f"✅ Completed! Added {updated} covers")

        print(f"\nSummary:\n  - Albums processed: {music_path}")
        print(f"  - Covers added: {updated}")
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
