#!/usr/bin/python3

"""
Script: Export Cover Art from MP3 Files

Description:
  This script automates cover art handling for MP3 albums. It compares embedded album artwork to any existing
  `cover.jpg` in the folder. If the embedded image is of higher resolution, it overwrites `cover.jpg`.
  Then, all embedded artwork is removed from MP3 files in the folder.

Features:
  - Compares embedded cover art with existing cover.jpg.
  - Keeps the higher resolution version in the filesystem as cover.jpg.
  - Removes embedded artwork from all MP3s in the folder.
  - Supports individual folders, full music library, or CD-specific folders.
  - Reads music library path from a config file (artwork-config.ini).

Requirements:
  - Python 3.x
  - External library: mutagen
  - Config file with a [paths] section containing 'rootmusicdir'.

Usage:
  Process a specific folder:
    python3 export-coverart.py -i "/path/to/album/folder/"

  Process the entire music library:
    python3 export-coverart.py -a

  Process CD folders in the entire library:
    python3 export-coverart.py -a -c
"""

import os
import sys
import argparse
import configparser
from io import BytesIO
from PIL import Image
from mutagen.id3 import ID3, ID3NoHeaderError

# Path to the configuration file
CONFIG_PATH = "artwork-config.ini"

# Read configuration settings from the ini file
config = configparser.ConfigParser()
config.read(CONFIG_PATH)

# Root music directory (read from the config file)
ROOT_MUSIC_DIR = config.get('paths', 'rootmusicdir', fallback='/media/william/NewData/Music/MP3B/')

def get_resolution_from_bytes(image_data):
    """Get width * height resolution of an image from raw byte data."""
    try:
        image = Image.open(BytesIO(image_data))
        return image.width * image.height
    except Exception:
        return 0

def read_cover_jpg_resolution(folder_path):
    """Return resolution (width * height) of cover.jpg, if present."""
    cover_path = os.path.join(folder_path, "cover.jpg")
    if os.path.exists(cover_path):
        try:
            with Image.open(cover_path) as img:
                return img.width * img.height
        except Exception:
            return 0
    return 0

def export_and_compare_cover(folder_path):
    """Export and compare embedded cover art to cover.jpg, keep highest res version."""
    mp3_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".mp3")]
    if not mp3_files:
        print(f"No MP3 files found in {folder_path}. Skipping...")
        return False

    # Read resolution of existing cover.jpg
    existing_res = read_cover_jpg_resolution(folder_path)
    best_apic = None
    best_res = 0

    # Find highest resolution APIC in the folder
    for mp3_file in mp3_files:
        mp3_path = os.path.join(folder_path, mp3_file)
        try:
            tags = ID3(mp3_path)
            for tag in tags.getall("APIC"):
                res = get_resolution_from_bytes(tag.data)
                if res > best_res:
                    best_res = res
                    best_apic = tag
        except Exception as e:
            print(f"Error reading artwork from {mp3_path}: {e}")

    if best_apic and best_res > existing_res:
        # Save higher-resolution embedded art as cover.jpg
        try:
            with open(os.path.join(folder_path, "cover.jpg"), "wb") as f:
                f.write(best_apic.data)
            print(f"Updated cover.jpg in {folder_path} with higher-resolution embedded art")
        except Exception as e:
            print(f"Failed to write new cover.jpg in {folder_path}: {e}")
    else:
        print(f"Existing cover.jpg in {folder_path} is higher or equal resolution. No update needed.")

    # Remove all embedded artwork after comparison
    remove_embedded_artwork_from_all(folder_path, mp3_files)
    return True

def remove_embedded_artwork(mp3_path):
    """Remove all embedded artwork (APIC frames) from a single MP3 file."""
    try:
        try:
            audio = ID3(mp3_path)
        except ID3NoHeaderError:
            audio = ID3()

        apic_count = len(audio.getall("APIC"))
        if apic_count > 0:
            audio.delall("APIC")
            audio.save(mp3_path, v2_version=3)
            print(f"Removed {apic_count} embedded artwork(s) from {mp3_path}")
        else:
            print(f"No embedded artwork found in {mp3_path}")
    except Exception as e:
        print(f"Error removing artwork from {mp3_path}: {e}")

def remove_embedded_artwork_from_all(folder_path, mp3_files):
    """Remove artwork from all MP3 files in the folder."""
    for mp3_file in mp3_files:
        full_path = os.path.join(folder_path, mp3_file)
        remove_embedded_artwork(full_path)

def process_folder(folder_path):
    """Process a folder: compare embedded and external cover art, keep highest resolution, and remove embedded art."""
    print(f"\nProcessing folder: {folder_path}")
    export_and_compare_cover(folder_path)

def process_cd_folders():
    """Process folders named like 'CD 1', 'CD 2', etc."""
    for root, dirs, _ in os.walk(ROOT_MUSIC_DIR):
        for dir_name in dirs:
            if dir_name.lower().startswith("cd "):
                folder_path = os.path.join(root, dir_name)
                process_folder(folder_path)

def main():
    """Parse command-line arguments and run cover processing."""
    parser = argparse.ArgumentParser(
        description="Export and compare MP3 cover art, keep highest res version and remove embedded artwork.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""Examples:
  Process a specific folder:
    python3 export-coverart.py -i "/media/william/NewData/Music/MP3B/Artist/Album/CD 1/"

  Process the entire library:
    python3 export-coverart.py -a

  Process CD folders only:
    python3 export-coverart.py -a -c
"""
    )

    parser.add_argument("-a", "--all", action="store_true", help="Process the entire music library.")
    parser.add_argument("-c", "--cd", action="store_true", help="Process CD folders only.")
    parser.add_argument("-i", "--input", type=str, help="Process a specific folder (album or CD folder).")

    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(1)

    if args.input:
        if not os.path.isdir(args.input):
            print(f"Error: {args.input} is not a valid directory.")
            sys.exit(1)
        process_folder(args.input)
    elif args.all:
        for root, dirs, _ in os.walk(ROOT_MUSIC_DIR):
            for dir_name in dirs:
                folder_path = os.path.join(root, dir_name)
                if args.cd:
                    if dir_name.lower().startswith("cd "):
                        process_folder(folder_path)
                else:
                    process_folder(folder_path)

if __name__ == "__main__":
    main()

