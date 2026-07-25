#!/usr/bin/env python3

"""
Script: Cover Art Cleanup
Purpose: Keeps the smaller of cover.jpg or cover.jpg.bak in album folders.
Logs output as: ✓ Artist - Album (action)
"""

import os
import sys
import logging
import configparser
import argparse

# Load configuration
def load_config():
    config = configparser.ConfigParser()
    config.read('artwork-config.ini')
    return config.get('paths', 'rootmusicdir', fallback=None)

# Logging setup (custom format)
LOG_FILE = "cover_cleanup.log"
logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
console_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))

logger.addHandler(file_handler)
logger.addHandler(console_handler)

def get_artist_album_from_path(folder_path):
    """Extract Artist and Album from folder path (e.g., /Music/Artist/Album)."""
    parts = os.path.normpath(folder_path).split(os.sep)
    if len(parts) >= 2:
        return parts[-2], parts[-1]  # Artist, Album
    return "Unknown Artist", "Unknown Album"

def cleanup_cover_pair(folder_path):
    """Keep the smaller of cover.jpg or cover.jpg.bak, delete the other."""
    cover_path = os.path.join(folder_path, "cover.jpg")
    cover_bak_path = os.path.join(folder_path, "cover.jpg.bak")

    if os.path.exists(cover_path) and os.path.exists(cover_bak_path):
        artist, album = get_artist_album_from_path(folder_path)
        cover_size = os.path.getsize(cover_path)
        cover_bak_size = os.path.getsize(cover_bak_path)

        if cover_bak_size < cover_size:
            os.remove(cover_path)
            os.rename(cover_bak_path, cover_path)
            logger.info(f"✓ {artist} - {album} (kept backup [smaller])")
        else:
            os.remove(cover_bak_path)
            logger.info(f"✓ {artist} - {album} (kept original [smaller])")

def process_folder(folder_path):
    """Process a single album folder."""
    cleanup_cover_pair(folder_path)

def process_all_folders(base_folder):
    """Recursively process all artist/album folders under base_folder."""
    for root, dirs, _ in os.walk(base_folder):
        for dir_name in dirs:
            folder_path = os.path.join(root, dir_name)
            if any(f.endswith('.mp3') for f in os.listdir(folder_path)):
                process_folder(folder_path)

def main():
    parser = argparse.ArgumentParser(
        description="Keep the smaller of cover.jpg or cover.jpg.bak, delete the other."
    )
    parser.add_argument("-i", "--input", type=str, help="Process a specific folder.")
    parser.add_argument("-a", "--all", action="store_true", help="Process all folders recursively.")
    parser.add_argument("-p", "--path", type=str, help="Override rootmusicdir from artwork-config.ini for this run.")
    args = parser.parse_args()

    root_music_dir = args.path or load_config()

    logger.info("🚀 Starting cover cleanup")

    if args.input:
        if not os.path.isdir(args.input):
            logger.error(f"💥 Error: {args.input} is not a directory.")
            sys.exit(1)
        process_folder(args.input)
    elif args.all:
        if not root_music_dir:
            logger.error("💥 Error: no music directory set. Use -p <folder> or set [paths] rootmusicdir in artwork-config.ini.")
            sys.exit(1)
        logger.info(f"📁 Root music directory: {root_music_dir}")
        process_all_folders(root_music_dir)
    else:
        logger.error("💥 Error: Use -i <folder> or -a for all folders.")
        sys.exit(1)

    logger.info("✅ Done!")

if __name__ == "__main__":
    main()
