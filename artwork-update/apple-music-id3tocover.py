#!/usr/bin/env python3

"""
Album Cover Updater with Real-Time Console Output
"""

import os
import sys
import signal
import logging
import argparse
import configparser
import requests
from mutagen.id3 import ID3, error as ID3Error
from PIL import Image
from pathlib import Path
import itunespy

# Configuration
CONFIG_FILE = "artwork-config.ini"
LOG_FILE = "apple-music-artwork.log"
CD_PREFIXES = ('cd', 'disc', 'disk')
REQUEST_TIMEOUT = 15  # seconds
MIN_FILE_SIZE = 50 * 1024  # 50KB minimum

# Global flag for graceful shutdown
should_exit = False

def signal_handler(sig, frame):
    global should_exit
    print("\n🛑 Received interrupt signal - shutting down...")
    should_exit = True
    signal.signal(signal.SIGINT, signal.SIG_DFL)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Update album artwork from Apple Music')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('-p', '--path', type=str, help='Override rootmusicdir from artwork-config.ini for this run.')
    parser.add_argument('-i', '--input', type=str, help='Process a specific folder (album or CD folder) instead of the whole library.')
    return parser.parse_args()

def setup_logging(debug=False):
    """Configure logging to show progress in console"""
    level = logging.DEBUG if debug else logging.INFO
    
    # Clear any existing handlers
    logging.getLogger().handlers = []
    
    # Create file handler (always used)
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    
    # Create console handler (always used)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
    
    # Apply configuration
    logging.basicConfig(
        level=level,
        handlers=[file_handler, console_handler]
    )

def load_config():
    """Load and validate configuration"""
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return {
        'music_path': config.get("paths", "rootmusicdir", fallback=None),
        'min_res': config.getint("settings", "MIN_RES", fallback=500)
    }

def is_cd_folder(name):
    """Check if folder is a CD subfolder"""
    return name.lower().startswith(CD_PREFIXES)

def get_artist_album_from_mp3(folder):
    """Extract metadata from first MP3 found"""
    for file in os.listdir(folder):
        if should_exit:
            return None, None
        if file.lower().endswith('.mp3'):
            try:
                audio = ID3(os.path.join(folder, file))
                artist = audio.get('TPE1').text[0] if 'TPE1' in audio else None
                album = audio.get('TALB').text[0] if 'TALB' in audio else None
                if artist and album:
                    return artist, album
            except ID3Error:
                continue
    return None, None

def has_mp3s(folder):
    """Check if folder contains MP3 files"""
    try:
        return any(f.lower().endswith('.mp3') for f in os.listdir(folder))
    except PermissionError:
        return False

def get_image_resolution(image_path):
    """Get resolution of image file"""
    try:
        with Image.open(image_path) as img:
            return img.size
    except Exception:
        return (0, 0)

def fetch_apple_music_artwork(artist, album):
    """Get artwork URL and resolution from Apple Music"""
    if should_exit:
        return None, (0, 0)
    try:
        results = itunespy.search_album(f"{artist} {album}")
        for result in results:
            if result.artist_name.lower() == artist.lower():
                url = result.artwork_url_100.replace("100x100bb.jpg", "1200x1200bb.jpg")
                return url, (1200, 1200)
    except Exception as e:
        logging.debug(f"API error: {str(e)}")
    return None, (0, 0)

def download_cover(artwork_url, save_path, expected_res=(1200,1200)):
    """Download and save cover image with resolution validation"""
    if should_exit:
        return False

    temp_path = f"{save_path}.tmp"
    try:
        # Download the image
        response = requests.get(artwork_url, stream=True, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        with open(temp_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if should_exit:
                    return False
                f.write(chunk)

        # Verify file size
        file_size = os.path.getsize(temp_path)
        if file_size < MIN_FILE_SIZE:
            logging.debug(f"Rejected small file: {file_size} bytes")
            os.remove(temp_path)
            return False

        # Verify actual resolution
        with Image.open(temp_path) as img:
            img.verify()
            actual_width, actual_height = img.size

        # Check if we should keep the new image
        if os.path.exists(save_path):
            with Image.open(save_path) as existing_img:
                existing_width, existing_height = existing_img.size
                existing_pixels = existing_width * existing_height
            new_pixels = actual_width * actual_height
            
            # Only replace if new image has significantly more pixels (10% threshold)
            if new_pixels <= existing_pixels * 1.1:
                os.remove(temp_path)
                return False

        # Save the new image
        if os.path.exists(save_path):
            os.remove(save_path)
        os.rename(temp_path, save_path)
        logging.debug(f"Accepted image: {actual_width}x{actual_height}")
        return True

    except Exception as e:
        logging.debug(f"Download failed: {str(e)}")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return False

def process_folder(folder, root_path=None):
    """Process a single album folder with proper console output.

    root_path is the walk's starting point, skipped so it isn't treated as
    an album itself. Pass None (as -i mode does) to process folder
    unconditionally.
    """
    if should_exit or (root_path is not None and Path(folder) == Path(root_path)) or not has_mp3s(folder):
        return False

    artist, album = get_artist_album_from_mp3(folder)
    if not artist or not album:
        logging.info(f"⚠️  No metadata found in: {os.path.basename(folder)}")
        return False

    cover_path = os.path.join(folder, 'cover.jpg')
    artwork_url, artwork_res = fetch_apple_music_artwork(artist, album)
    
    if not artwork_url:
        logging.info(f"❌ No artwork found for: {artist} - {album}")
        return False
    
    existing_cover = os.path.exists(cover_path)
    existing_res = get_image_resolution(cover_path) if existing_cover else (0, 0)
    
    if download_cover(artwork_url, cover_path, artwork_res):
        with Image.open(cover_path) as img:
            new_res = img.size
        
        if not existing_cover:
            logging.info(f"✅ Added cover: {artist} - {album} ({new_res[0]}x{new_res[1]})")
            return True
        else:
            logging.info(f"🔼 Upgraded cover: {artist} - {album} ({existing_res[0]}x{existing_res[1]} → {new_res[0]}x{new_res[1]})")
            return True
    elif existing_cover:
        logging.info(f"⏩ Skipping: {artist} - {album} (existing cover {existing_res[0]}x{existing_res[1]} is sufficient)")
    
    return False

def main():
    """Main processing loop"""
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, signal_handler)

    args = parse_args()
    setup_logging(debug=args.debug)

    try:
        logging.info("🚀 Starting Apple Music cover art update")

        updated = 0
        if args.input:
            if not os.path.isdir(args.input):
                logging.error(f"💥 Error: {args.input} is not a valid directory.")
                sys.exit(1)
            if process_folder(args.input):
                updated += 1
        else:
            config = load_config()
            music_path_str = args.path or config['music_path']
            if not music_path_str:
                logging.error("💥 Error: no music directory set. Use -p <folder> or set [paths] rootmusicdir in artwork-config.ini.")
                sys.exit(1)
            music_path = Path(music_path_str)

            logging.info(f"📁 Scanning: {music_path}")

            for root, dirs, _ in os.walk(music_path):
                if should_exit:
                    break
                if process_folder(root, music_path):
                    updated += 1
                for dir_name in filter(is_cd_folder, dirs):
                    if should_exit:
                        break
                    cd_path = os.path.join(root, dir_name)
                    if process_folder(cd_path, music_path):
                        updated += 1

        logging.info(f"\n✅ Completed! Updated {updated} covers")
        logging.info(f"Summary:\n  - Covers updated: {updated}\n  - Log: {LOG_FILE}")

    except Exception as e:
        logging.error(f"💥 Error: {str(e)}")
    finally:
        signal.signal(signal.SIGINT, original_sigint)

if __name__ == '__main__':
    main()
