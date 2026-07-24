#!/usr/bin/env python3

"""
Script: MusicBrainz Cover Art Fetcher
"""

import os
import sys
import logging
import configparser
import requests
import argparse
import shutil
from mutagen.id3 import ID3, error as ID3Error
from PIL import Image, ImageFile
import musicbrainzngs
import warnings
import tempfile
from urllib.error import HTTPError

# Configure musicbrainzngs to suppress specific warnings
warnings.filterwarnings("ignore", category=UserWarning, module="musicbrainzngs")

# Load configuration
config = configparser.ConfigParser()
config.read('artwork-config.ini')

# Validate configuration
def validate_config(config):
    required_fields = {
        "settings": ["MIN_RES"],
        "paths": ["rootmusicdir"],
    }
    for section, fields in required_fields.items():
        if section not in config:
            print(f"Error: Missing section '{section}' in config file.")
            sys.exit(1)
        for field in fields:
            if field not in config[section]:
                print(f"Error: Missing '{field}' in section '{section}' in config file.")
                sys.exit(1)

validate_config(config)

# Custom logging filter
class MusicBrainzWarningFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        return not msg.startswith("in <ws2:release-group>, uncaught attribute type-id")

# Logging setup
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mb-cca-artwork.log")
logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.INFO)
file_handler.addFilter(MusicBrainzWarningFilter())
file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.addFilter(MusicBrainzWarningFilter())
console_formatter = logging.Formatter("%(levelname)s - %(message)s")
console_handler.setFormatter(console_formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Settings
MIN_RES = int(config["settings"]["MIN_RES"])
ROOT_MUSIC_DIR = config["paths"]["rootmusicdir"]

# Setup MusicBrainz
musicbrainzngs.set_useragent("ID3ToCover", "1.0", "https://example.com")

# Increase PIL's buffer size to handle large images
ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = None  # Remove limit on image size

def fetch_mb_cca_artwork(artist, album):
    try:
        results = musicbrainzngs.search_releases(artist=artist, release=album, limit=1)
        if results['release-list']:
            release = results['release-list'][0]
            mbid = release['id']
            try:
                art = musicbrainzngs.get_image_list(mbid)
                if 'images' in art:
                    for image in art['images']:
                        if image.get("front", False) and image.get("image"):
                            return image["image"]
                logger.info(f"✗ {artist} - {album} (no artwork found)")
                return None
            except HTTPError as e:
                if e.code == 404:
                    logger.info(f"✗ {artist} - {album} (no artwork found)")
                    return None
                raise
            except Exception:
                logger.info(f"✗ {artist} - {album} (no artwork found)")
                return None
        logger.info(f"✗ {artist} - {album} (no artwork found)")
        return None
    except Exception:
        # Catch any other MusicBrainz API errors
        logger.info(f"✗ {artist} - {album} (no artwork found)")
        return None

def download_artwork(url, save_path):
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        if 'image' not in response.headers.get('Content-Type', ''):
            return False
        
        # Create a temporary file in the same directory as the destination
        temp_dir = os.path.dirname(save_path)
        with tempfile.NamedTemporaryFile(dir=temp_dir, delete=False, suffix='.jpg') as tmp_file:
            for chunk in response.iter_content(chunk_size=8192):
                tmp_file.write(chunk)
            tmp_path = tmp_file.name
        
        # Verify the image can be opened before using it
        try:
            with Image.open(tmp_path) as img:
                img.verify()  # Verify it's a valid image
            # Use shutil.move instead of os.replace for cross-device support
            shutil.move(tmp_path, save_path)
            return True
        except Exception as e:
            logger.warning(f"Invalid image downloaded: {e}")
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            return False
            
    except Exception as e:
        logger.warning(f"Error downloading artwork: {e}")
        return False

def get_artist_album_from_id3(file_path):
    try:
        audio = ID3(file_path)
        artist_tag = audio.get('TPE1')
        artist = artist_tag.text[0] if artist_tag else "Unknown Artist"
        album_tag = audio.get('TALB')
        album = album_tag.text[0] if album_tag else "Unknown Album"
        return artist, album
    except ID3Error:
        return "Unknown Artist", "Unknown Album"

def meets_resolution(image_path, min_res):
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            return width >= min_res and height >= min_res
    except Exception as e:
        logger.warning(f"Error checking image resolution: {e}")
        return False

def process_folder(folder_path):
    try:
        cover_path = os.path.join(folder_path, "cover.jpg")
        mp3_files = [f for f in os.listdir(folder_path) if f.endswith(".mp3")]
        if not mp3_files:
            logger.warning(f"No MP3 files found in {folder_path}")
            return

        first_mp3 = os.path.join(folder_path, mp3_files[0])
        artist, album = get_artist_album_from_id3(first_mp3)

        artwork_url = fetch_mb_cca_artwork(artist, album)

        if artwork_url:
            temp_artwork_path = os.path.join(folder_path, "temp_cover.jpg")
            if download_artwork(artwork_url, temp_artwork_path):
                try:
                    if not os.path.exists(cover_path):
                        shutil.move(temp_artwork_path, cover_path)
                        logger.info(f"↑ {artist} - {album} (added cover)")
                    else:
                        try:
                            with Image.open(cover_path) as existing_image, Image.open(temp_artwork_path) as downloaded_image:
                                if downloaded_image.size > existing_image.size or not meets_resolution(cover_path, MIN_RES):
                                    shutil.move(temp_artwork_path, cover_path)
                                    logger.info(f"↑ {artist} - {album} (replaced cover)")
                                else:
                                    os.remove(temp_artwork_path)
                                    logger.info(f"✓ {artist} - {album} (kept existing cover)")
                        except Exception as e:
                            logger.warning(f"Error comparing images: {e}")
                            if os.path.exists(temp_artwork_path):
                                os.remove(temp_artwork_path)
                except Exception as e:
                    logger.warning(f"Error processing artwork for {artist} - {album}: {e}")
                    if os.path.exists(temp_artwork_path):
                        os.remove(temp_artwork_path)
    except KeyboardInterrupt:
        raise  # Re-raise KeyboardInterrupt to stop the script
    except Exception as e:
        logger.error(f"Unexpected error processing folder {folder_path}: {e}")

def process_all_folders(base_folder):
    try:
        for artist_folder in os.listdir(base_folder):
            artist_path = os.path.join(base_folder, artist_folder)
            if os.path.isdir(artist_path):
                for album_folder in os.listdir(artist_path):
                    album_path = os.path.join(artist_path, album_folder)
                    if os.path.isdir(album_path):
                        cd_subfolders = [f for f in os.listdir(album_path) if os.path.isdir(os.path.join(album_path, f)) and f.lower().startswith('cd ')]
                        if cd_subfolders:
                            for cd_folder in cd_subfolders:
                                cd_path = os.path.join(album_path, cd_folder)
                                process_folder(cd_path)
                        else:
                            process_folder(album_path)
    except KeyboardInterrupt:
        logger.info("🛑 Script interrupted by user")
        sys.exit(0)

def main():
    parser = argparse.ArgumentParser(
        description="Fetch album artwork from MusicBrainz Cover Art Archive and save it as cover.jpg."
    )
    parser.add_argument("-i", "--input", type=str, help="Process a specific folder (album folder).")
    parser.add_argument("-a", "--all", action="store_true", help="Process the entire music library.")
    args = parser.parse_args()

    logger.info("🚀 Starting MusicBrainz Cover Art Archive cover art update")
    logger.info(f"📁 Scanning: {ROOT_MUSIC_DIR}")

    try:
        if args.input:
            if not os.path.isdir(args.input):
                logger.error(f"💥 Error: {args.input} is not a valid directory.")
                sys.exit(1)
            process_folder(args.input)
        elif args.all:
            process_all_folders(ROOT_MUSIC_DIR)
        else:
            logger.error("💥 Error: Please specify either -i <folder> or -a to process all folders.")
            sys.exit(1)

        logger.info("✅ Completed!")
    except KeyboardInterrupt:
        logger.info("🛑 Script interrupted by user")
        sys.exit(0)

if __name__ == "__main__":
    main()
