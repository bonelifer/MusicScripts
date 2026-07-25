#!/usr/bin/env python3

"""
Script: root_cover_remover.py
Description: Removes cover.jpg ONLY from album root folders while preserving them in CD subfolders
"""

import os
import sys
import logging
import configparser
import argparse

# Load configuration
config = configparser.ConfigParser()
config.read('artwork-config.ini')

# Logging setup
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cover-cleanup.log")
logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter("%(levelname)s - %(message)s")
console_handler.setFormatter(console_formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

def is_cd_subfolder(path):
    """Check if path is a CD subfolder"""
    folder_name = os.path.basename(path).lower()
    return folder_name.startswith(('cd ', 'disc ')) or any(
        x in folder_name for x in ['cd', 'disc', 'disk'])

def main():
    parser = argparse.ArgumentParser(
        description="Remove cover.jpg ONLY from album root folders while preserving CD subfolder covers"
    )
    parser.add_argument("--confirm", action="store_true", help="Actually perform deletions (dry run by default)")
    parser.add_argument("-p", "--path", type=str, help="Override rootmusicdir from artwork-config.ini for this run.")
    args = parser.parse_args()

    root_music_dir = args.path or config.get("paths", "rootmusicdir", fallback=None)
    if not root_music_dir:
        logger.error("💥 Error: no music directory set. Use -p <folder> or set [paths] rootmusicdir in artwork-config.ini.")
        sys.exit(1)

    logger.info("🚀 Starting Remove Cover Art from Album Root cleanup")
    logger.info(f"📁 Root music directory: {root_music_dir}")

    if not args.confirm:
        logger.info("⚠️ Running in dry-run mode (use --confirm to actually delete files)")

    try:
        for root, dirs, files in os.walk(root_music_dir):
            # Skip processing if this is a CD subfolder
            if is_cd_subfolder(root):
                continue
                
            # Only process cover.jpg in the current directory (not subfolders)
            if "cover.jpg" in files:
                cover_path = os.path.join(root, "cover.jpg")
                
                if args.confirm:
                    try:
                        os.remove(cover_path)
                        logger.info(f"Removed root cover: {cover_path}")
                    except Exception as e:
                        logger.error(f"Failed to remove {cover_path}: {e}")
                else:
                    logger.info(f"Would remove root cover: {cover_path}")

        logger.info("✅ Cleanup completed!")
        if not args.confirm:
            logger.info("⚠️ Remember to run with --confirm to actually delete files")

    except KeyboardInterrupt:
        logger.info("🛑 Script interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
