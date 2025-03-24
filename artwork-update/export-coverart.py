#!/usr/bin/python3

"""
Script: Export Cover Art from MP3 Files

Description:
  This script automates the process of extracting and saving album cover art embedded in MP3 files.
  It searches for cover art in the ID3 tags of MP3 files and saves it as `cover.jpg` in the same folder.
  The script can process a specific folder, an entire music library, or only CD folders (e.g., CD 1, CD 2).

Features:
  - Extracts cover art from the first MP3 file in a folder.
  - Saves the extracted cover art as `cover.jpg` in the same folder.
  - Processes specific folders, entire music libraries, or only CD folders.
  - Skips folders where `cover.jpg` already exists.
  - Reads the root music directory from a configuration file.

Requirements:
  - Python 3.x
  - External libraries: mutagen
  - Configuration file (artwork-config.ini) with the `rootmusicdir` field under the `paths` section.

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
from mutagen.id3 import ID3, APIC

# Path to the configuration file
CONFIG_PATH = "artwork-config.ini"

# Read configuration settings from the ini file
config = configparser.ConfigParser()
config.read(CONFIG_PATH)

# Root music directory (read from the config file)
ROOT_MUSIC_DIR = config.get('paths', 'rootmusicdir', fallback='/media/william/NewData/Music/MP3B/')

def export_cover_from_mp3(folder_path):
    """Export cover art from the first MP3 file in the folder and save it as cover.jpg."""
    music_files = [f for f in os.listdir(folder_path) if f.endswith(".mp3")]
    if not music_files:
        print(f"No MP3 files found in {folder_path}. Skipping...")
        return False

    first_mp3 = os.path.join(folder_path, music_files[0])
    try:
        audio_file = ID3(first_mp3)
        for tag in audio_file.values():
            if isinstance(tag, APIC):  # Check if the tag is artwork (APIC)
                with open(os.path.join(folder_path, "cover.jpg"), "wb") as cover_file:
                    cover_file.write(tag.data)
                print(f"Exported cover art from {first_mp3} to {folder_path}/cover.jpg")
                return True
    except Exception as e:
        print(f"Error processing {first_mp3}: {e}")
    return False

def process_folder(folder_path):
    """Process a single folder to check for cover.jpg or export it from an MP3."""
    cover_path = os.path.join(folder_path, "cover.jpg")
    
    if not os.path.exists(cover_path):
        print(f"Cover image not found in {folder_path}. Attempting to export from MP3...")
        if not export_cover_from_mp3(folder_path):
            print(f"Could not export cover art from MP3 in {folder_path}. Skipping...")
    else:
        print(f"Cover image already exists in {folder_path}. Skipping...")

def process_cd_folders():
    """Process only CD folders (e.g., CD 1, CD 2)."""
    for root, dirs, files in os.walk(ROOT_MUSIC_DIR):
        for dir_name in dirs:
            if dir_name.startswith("CD "):  # Looking for directories named "CD 1", "CD 2", etc.
                folder_path = os.path.join(root, dir_name)
                process_folder(folder_path)

def main():
    """Main function to handle argument parsing and execution."""
    parser = argparse.ArgumentParser(
        description="Export cover art from MP3 files to cover.jpg.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""Examples:
  Process a specific folder:
    python3 export-coverart.py -i "/media/william/NewData/Music/MP3B/Zac Brown Band/Uncaged (2012)/CD 1/"

  Process the entire library:
    python3 export-coverart.py -a

  Process CD folders in the entire library:
    python3 export-coverart.py -a -c
"""
    )

    parser.add_argument("-a", "--all", action="store_true", help="Process the entire music library.")
    parser.add_argument("-c", "--cd", action="store_true", help="Process CD folders (e.g., CD 1, CD 2).")
    parser.add_argument("-i", "--input", type=str, help="Process a specific folder (album or CD folder).")

    args = parser.parse_args()

    # Check if no arguments were passed
    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(1)

    if args.input:
        # Process the specified folder
        if not os.path.isdir(args.input):
            print(f"Error: {args.input} is not a valid directory.")
            sys.exit(1)

        process_folder(args.input)
    elif args.all:
        # Process the entire music library recursively
        for root, dirs, files in os.walk(ROOT_MUSIC_DIR):
            for dir_name in dirs:
                folder_path = os.path.join(root, dir_name)
                process_folder(folder_path)
    elif args.cd:
        # Process only CD folders
        process_cd_folders()

if __name__ == "__main__":
    main()
