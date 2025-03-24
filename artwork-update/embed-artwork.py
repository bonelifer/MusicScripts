#!/usr/bin/python3

"""
Script: Embed and Check Artwork Resolution in Music Files

Description:
  This script automates the process of embedding and checking the resolution of album cover art in MP3 files.
  It ensures that the embedded artwork meets a specified resolution (TEMP_RES) and resizes the artwork if necessary.
  The script can process a specific folder, an entire music library, or only CD folders (e.g., CD 1, CD 2).

Features:
  - Checks the resolution of existing cover art (`cover.jpg`) in folders.
  - Resizes cover art to a specified resolution (TEMP_RES) if it exceeds the limit.
  - Converts non-JPEG images to JPEG format.
  - Embeds resized or original cover art into MP3 files.
  - Removes existing embedded artwork if it has a lower resolution than the new artwork.
  - Processes specific folders, entire music libraries, or only CD folders.

Requirements:
  - Python 3.x
  - External libraries: mutagen, pillow
  - Configuration file (artwork-config.ini) with the `rootmusicdir` field under the `paths` section and `TEMP_RES` under `cover_art_script`.

Usage:
  Process a specific folder:
    python3 embed-artwork.py -i "/path/to/album/folder/"

  Process the entire music library:
    python3 embed-artwork.py -a

  Process CD folders in the entire library:
    python3 embed-artwork.py -a -c
"""

import os
import sys
import io
import argparse
import configparser
from PIL import Image
from mutagen.id3 import ID3, APIC

# Constants for configuration paths and temp resolution
CONFIG_PATH = "artwork-config.ini"

# Read configuration settings from the ini file
config = configparser.ConfigParser()
config.read(CONFIG_PATH)

# Get temp resolution setting from config
TEMP_RES = int(config.get('cover_art_script', 'TEMP_RES', fallback=600))

# Root music directory (this can be adjusted based on your setup)
ROOT_MUSIC_DIR = config.get('paths', 'rootmusicdir', fallback='/media/william/NewData/Music/MP3B/')

# Helper functions
def check_cover_resolution(cover_path):
    """Check resolution of cover.jpg and return width, height."""
    with Image.open(cover_path) as img:
        return img.size

def create_temp_cover(original_cover_path, temp_res=TEMP_RES):
    """Create a temporary resized cover image."""
    with Image.open(original_cover_path) as img:
        # Convert RGBA or P to RGB if necessary
        if img.mode in ['RGBA', 'P']:
            img = img.convert('RGB')
        
        # Resize to temp resolution but don't upscale if original is smaller
        if img.width >= temp_res and img.height >= temp_res:
            img = img.resize((temp_res, temp_res))
        temp_path = "/tmp/temp_cover.jpg"
        img.save(temp_path)
        return temp_path

def get_embedded_artwork_resolution(audio_file):
    """Get the resolution of the embedded artwork in the MP3 file."""
    for tag in audio_file.values():
        if isinstance(tag, APIC):  # Check if the tag is artwork (APIC)
            with Image.open(io.BytesIO(tag.data)) as img:
                return img.size
    return None  # No embedded artwork found

def remove_artwork(audio_file):
    """Remove all embedded artwork (APIC tags) from the MP3 file."""
    artwork_removed = False
    for tag in list(audio_file.keys()):
        if tag.startswith("APIC"):  # Check if the tag is an APIC tag
            del audio_file[tag]  # Delete the artwork tag
            artwork_removed = True
            print(f"Removed embedded artwork from {audio_file.filename}.")
    return artwork_removed

def process_folder(folder_path):
    """Process a single folder to embed artwork."""
    cover_path = os.path.join(folder_path, "cover.jpg")
    
    if not os.path.exists(cover_path):
        print(f"Cover image not found in {folder_path}. Skipping...")
        return
    
    # Check if the file is empty
    if os.path.getsize(cover_path) == 0:
        print(f"Cover image in {folder_path} is empty. Skipping...")
        return
    
    try:
        # Open the image to verify its format and integrity
        with Image.open(cover_path) as img:
            img.verify()  # Verify that the file is a valid image
            img_format = img.format  # Get the actual format of the image
            print(f"Found cover image in {folder_path} with format: {img_format}")
            
            # If the image is not a JPEG, convert it to JPEG
            if img_format != "JPEG":
                print(f"Converting {img_format} image to JPEG...")
                img = Image.open(cover_path)  # Reopen the image for processing
                if img.mode in ['RGBA', 'P']:  # Convert RGBA or P mode to RGB
                    img = img.convert('RGB')
                temp_cover_path = "/tmp/temp_cover.jpg"
                img.save(temp_cover_path, format="JPEG")
                print(f"Converted cover image saved to {temp_cover_path}")
            else:
                temp_cover_path = cover_path
    except Exception as e:
        print(f"Cover image in {folder_path} is invalid or unsupported: {e}. Skipping...")
        return
    
    # Check the resolution of the cover.jpg
    try:
        cover_width, cover_height = check_cover_resolution(cover_path)
    except Exception as e:
        print(f"Error checking resolution of cover image in {folder_path}: {e}. Skipping...")
        return
    
    # If the cover.jpg is smaller than the temp resolution, use it as-is
    if cover_width < TEMP_RES and cover_height < TEMP_RES:
        print(f"Cover image in {folder_path} is already smaller than the temp resolution. Using original cover.")
        temp_cover_path = cover_path
    else:
        # Resize the cover image
        try:
            temp_cover_path = create_temp_cover(cover_path)
            print(f"Created resized cover image at {temp_cover_path}.")
        except Exception as e:
            print(f"Error resizing cover image in {folder_path}: {e}. Skipping...")
            return

    # Process the embedded artwork (assuming we're handling MP3 files here)
    music_files = [f for f in os.listdir(folder_path) if f.endswith(".mp3")]
    
    for music_file in music_files:
        music_path = os.path.join(folder_path, music_file)
        print(f"Processing {music_path}...")

        try:
            audio_file = ID3(music_path)
            
            # Check if there is embedded artwork and get its resolution
            embedded_resolution = get_embedded_artwork_resolution(audio_file)
            if embedded_resolution:
                embedded_width, embedded_height = embedded_resolution
                print(f"Found embedded artwork with resolution {embedded_width}x{embedded_height}.")

                # Compare embedded artwork resolution with the new artwork
                with Image.open(temp_cover_path) as new_artwork:
                    new_width, new_height = new_artwork.size
                    if embedded_width >= new_width and embedded_height >= new_height:
                        print(f"Embedded artwork has higher or equal resolution. Skipping embedding.")
                        continue  # Skip embedding if embedded artwork is better

            # Remove any existing artwork
            artwork_removed = remove_artwork(audio_file)
            
            # Embed the new artwork
            with open(temp_cover_path, "rb") as cover_file:
                cover_data = cover_file.read()
            audio_file.add(APIC(
                encoding=3,  # UTF-8 encoding
                mime="image/jpeg",
                type=3,  # Front cover
                desc="Cover",
                data=cover_data
            ))
            audio_file.save()
            print(f"Embedded artwork in {music_path}")
        except Exception as e:
            print(f"Error processing {music_path}: {e}")

def embed_artwork_in_folder(folder_path, recursive=False):
    """Process the folder to embed resized cover art or embed cover.jpg if no embedded artwork exists."""
    if recursive:
        # Recursively process all subdirectories
        for root, dirs, files in os.walk(folder_path):
            for dir_name in dirs:
                process_folder(os.path.join(root, dir_name))
    else:
        # Process only the specified folder
        process_folder(folder_path)

def process_cd_folders():
    """Process only CD folders (e.g., CD 1, CD 2)."""
    for root, dirs, files in os.walk(ROOT_MUSIC_DIR):
        for dir_name in dirs:
            if dir_name.startswith("CD "):  # Looking for directories named "CD 1", "CD 2", etc.
                folder_path = os.path.join(root, dir_name)
                embed_artwork_in_folder(folder_path)

def main():
    # Argument parsing setup
    parser = argparse.ArgumentParser(
        description="Embed and check artwork resolution in music files.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""Examples:
  Process a specific folder:
    python3 embed-artwork.py -i "/media/william/NewData/Music/MP3B/Zac Brown Band/Uncaged (2012)/CD 1/"

  Process the entire library:
    python3 embed-artwork.py -a

  Process CD folders in the entire library:
    python3 embed-artwork.py -a -c
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

        embed_artwork_in_folder(args.input)
    elif args.all:
        # Process the entire music library recursively
        embed_artwork_in_folder(ROOT_MUSIC_DIR, recursive=True)
    elif args.cd:
        # Process only CD folders
        process_cd_folders()

if __name__ == "__main__":
    main()
