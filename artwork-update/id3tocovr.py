#!/usr/bin/env python3

"""
Script: Album Artwork Fetcher

Description:
  This script automates the process of fetching album artwork for music files stored in a specified directory.
  It supports fetching artwork from multiple sources, including iTunes, MusicBrainz, and Last.fm.
  The script reads configuration from an INI file and allows for high-resolution artwork fetching.
  It is designed to handle large music libraries and can process both album folders and CD subfolders.

Features:
  - Fetches artwork from iTunes, MusicBrainz (Cover Art Archive), and Last.fm.
  - Supports high-resolution artwork fetching with configurable minimum resolution.
  - Handles ID3 tags to extract artist and album information.
  - Logs all actions and errors for troubleshooting.
  - Configurable via an INI file (artwork-config.ini).
  - Processes entire music libraries or specific folders.
  - Supports CD subfolders (e.g., CD 1, CD 2) for multi-disc albums.

Requirements:
  - Python 3.x
  - External libraries: mutagen, pillow, itunespy, musicbrainzngs, pylast, requests
  - Configuration file (artwork-config.ini) with required fields.
  - Internet connection for fetching artwork from online sources.

Usage:
  Process a specific folder:
    python3 id3tocovr.py -i "/path/to/album/folder/"

  Process a specific CD folder:
    python3 id3tocovr.py -i "/path/to/album/folder/CD 1/"

  Process the entire music library:
    python3 id3tocovr.py -a

  Process CD folders in the entire library:
    python3 id3tocovr.py -a -c
"""

import os
import sys
import logging
import configparser
import requests
import argparse
from mutagen.id3 import ID3, error as ID3Error
from PIL import Image
import itunespy
import musicbrainzngs
import pylast

# Load configuration from artwork-config.ini
config = configparser.ConfigParser()
config.read('artwork-config.ini')

# Validate configuration
def validate_config(config):
    """
    Validate the INI configuration file to ensure all required fields and sections are present.
    If any required field is missing, the script will exit with an error message.
    """
    required_fields = {
        "musicbrainz": ["useragent_email"],
        "credentials": ["lastfm-apikey"],
        "settings": ["USE_HIRES", "MIN_RES", "USE_FALLBACK", "USE_HIRES_PRIORITY", "USE_MUSICBRAINZ", "NO_LOW_RES"],
        "paths": ["rootmusicdir"],
    }

    # Check for missing sections or fields
    for section, fields in required_fields.items():
        if section not in config:
            print(f"Error: Missing section '{section}' in config file.")
            sys.exit(1)
        for field in fields:
            if field not in config[section]:
                print(f"Error: Missing '{field}' in section '{section}' in config file.")
                sys.exit(1)

# Validate the configuration file before proceeding
validate_config(config)

# Logging setup
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "album-artwork.log")
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# MusicBrainz setup
musicbrainzngs.set_useragent(
    "album-artwork-fetcher",  # Application name
    "0.1",                   # Application version
    config["musicbrainz"]["useragent_email"]  # User's email
)

# Last.fm setup
lastfm_network = pylast.LastFMNetwork(api_key=config["credentials"]["lastfm-apikey"])

# Settings
USE_HIRES = config["settings"].getboolean("USE_HIRES")
MIN_RES = int(config["settings"]["MIN_RES"])
USE_FALLBACK = config["settings"].getboolean("USE_FALLBACK")
USE_HIRES_PRIORITY = config["settings"].getboolean("USE_HIRES_PRIORITY")
USE_MUSICBRAINZ = config["settings"].getboolean("USE_MUSICBRAINZ")
NO_LOW_RES = config["settings"].getboolean("NO_LOW_RES")

# Root music directory
ROOT_MUSIC_DIR = config["paths"]["rootmusicdir"]

# Functions
def get_artist_album_from_id3(file_path):
    """
    Extract artist and album from the ID3 tags of the file.
    Handles cases where tags are strings or Frame objects.
    """
    try:
        audio = ID3(file_path)
        
        # Get artist (TPE1 tag)
        artist_tag = audio.get('TPE1')
        if artist_tag:
            artist = artist_tag.text[0] if hasattr(artist_tag, 'text') else str(artist_tag)
        else:
            artist = "Unknown Artist"

        # Get album (TALB tag)
        album_tag = audio.get('TALB')
        if album_tag:
            album = album_tag.text[0] if hasattr(album_tag, 'text') else str(album_tag)
        else:
            album = "Unknown Album"

        return artist, album
    except ID3Error as e:
        logging.error(f"Failed to read ID3 tags from {file_path}: {e}")
        return "Unknown Artist", "Unknown Album"

def fetch_itunes_artwork(artist, album):
    """Fetch album art from iTunes using itunespy."""
    try:
        results = itunespy.search_album(album)
        for result in results:
            if result.artist_name.lower() == artist.lower():
                return result.artwork_url_600  # High-resolution artwork
    except Exception as e:
        logging.error(f"Failed to fetch iTunes artwork: {e}")
    return None

def fetch_musicbrainz_release_id(artist, album):
    """Fetch the release ID for an album from MusicBrainz."""
    try:
        results = musicbrainzngs.search_releases(artist=artist, release=album, limit=1)
        if results and "release-list" in results:
            return results["release-list"][0]["id"]  # Return the first matching release ID
    except Exception as e:
        logging.error(f"Failed to fetch MusicBrainz release ID: {e}")
    return None

def fetch_caa_artwork(release_id):
    """Fetch album artwork from the Cover Art Archive."""
    try:
        url = f"https://coverartarchive.org/release/{release_id}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if "images" in data:
            for image in data["images"]:
                if image["front"]:  # Prioritize front cover art
                    return image["image"]  # URL of the highest-resolution image
    except Exception as e:
        logging.error(f"Failed to fetch Cover Art Archive artwork: {e}")
    return None

def fetch_lastfm_artwork(artist, album):
    """Fetch album art from Last.fm using pylast."""
    if NO_LOW_RES:
        print("Skipping Last.fm artwork fetching (NO_LOW_RES is enabled).")
        logging.info("Skipping Last.fm artwork fetching (NO_LOW_RES is enabled).")
        return None

    try:
        album_info = lastfm_network.get_album(artist, album)
        return album_info.get_cover_image(size=pylast.SIZE_LARGE)  # Large-size artwork
    except Exception as e:
        logging.error(f"Failed to fetch Last.fm artwork: {e}")
    return None

def download_artwork(url, save_path):
    """Download artwork from a URL and save it to the specified path."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Check if the response is an image
        if 'image' not in response.headers.get('Content-Type', ''):
            logging.error(f"URL does not point to an image: {url}")
            return False

        with open(save_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        logging.info(f"Artwork saved to {save_path}")
        return True
    except Exception as e:
        logging.error(f"Failed to download artwork: {e}")
        return False

def meets_resolution(image_path, min_res):
    """Check if an image meets the minimum resolution requirement."""
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            return width >= min_res and height >= min_res
    except Exception:
        return False

def fetch_artwork_for_folder(folder_path):
    """
    Fetch artwork for a folder (album or CD folder).
    """
    cover_path = os.path.join(folder_path, "cover.jpg")

    # Skip if cover.jpg already exists
    if os.path.exists(cover_path):
        print(f"Skipping {folder_path}: cover.jpg already exists.")
        logging.info(f"Skipping {folder_path}: cover.jpg already exists.")
        return

    # Find the first MP3 file in the folder
    mp3_files = [f for f in os.listdir(folder_path) if f.endswith(".mp3")]
    if not mp3_files:
        print(f"No MP3 files found in {folder_path}")
        logging.warning(f"No MP3 files found in {folder_path}")
        return

    # Get artist and album from the first MP3 file's ID3 tags
    first_mp3 = os.path.join(folder_path, mp3_files[0])
    artist, album = get_artist_album_from_id3(first_mp3)
    print(f"Processing folder: {folder_path}, Artist: {artist}, Album: {album}")

    # Fetch artwork from various sources
    artwork_url = None
    if USE_MUSICBRAINZ:
        release_id = fetch_musicbrainz_release_id(artist, album)
        if release_id:
            artwork_url = fetch_caa_artwork(release_id)

    if not artwork_url and USE_HIRES_PRIORITY:
        artwork_url = fetch_itunes_artwork(artist, album)

    if not artwork_url and not NO_LOW_RES:
        artwork_url = fetch_lastfm_artwork(artist, album)

    # Save artwork to the folder
    if artwork_url:
        if download_artwork(artwork_url, cover_path):
            print(f"Artwork saved for {artist} - {album} at {cover_path}")
            logging.info(f"Artwork saved for {artist} - {album} at {cover_path}")
        else:
            print(f"Failed to download artwork for {artist} - {album}")
            logging.error(f"Failed to download artwork for {artist} - {album}")
    else:
        print(f"No artwork found for {artist} - {album}")
        logging.warning(f"No artwork found for {artist} - {album}")

def process_folder(root_folder, process_cd_folders=False):
    """
    Process all subfolders in the given root folder and fetch artwork for each album.
    If process_cd_folders is True, process CD folders. Otherwise, process the root album folder.
    """
    # Get a list of artist folders and sort them alphabetically
    artist_folders = [f for f in os.listdir(root_folder) if os.path.isdir(os.path.join(root_folder, f))]
    artist_folders.sort()

    for artist_folder in artist_folders:
        artist_path = os.path.join(root_folder, artist_folder)
        print(f"Processing artist: {artist_folder}")

        # Process each album folder under the artist
        for album_folder in os.listdir(artist_path):
            album_path = os.path.join(artist_path, album_folder)
            if not os.path.isdir(album_path):
                continue

            # Check if this album folder has CD subfolders
            cd_folders = [f for f in os.listdir(album_path) if os.path.isdir(os.path.join(album_path, f)) and f.lower().startswith("cd")]

            if process_cd_folders and cd_folders:
                # Process each CD folder
                for cd_folder in cd_folders:
                    cd_path = os.path.join(album_path, cd_folder)
                    fetch_artwork_for_folder(cd_path)
            else:
                # Process the album folder itself
                fetch_artwork_for_folder(album_path)

def main():
    """Main function to process the root music directory or a specific folder."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Fetch album artwork for music files.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""Examples:
  Process a specific folder:
    python3 id3tocovr.py -i "/path/to/album/folder/"

  Process a specific CD folder:
    python3 id3tocovr.py -i "/path/to/album/folder/CD 1/"

  Process the entire music library:
    python3 id3tocovr.py -a

  Process CD folders in the entire library:
    python3 id3tocovr.py -a -c
"""
    )
    parser.add_argument("-a", "--all", action="store_true", help="Process the entire music library.")
    parser.add_argument("-c", "--cd", action="store_true", help="Process CD folders (e.g., CD 1, CD 2).")
    parser.add_argument("-i", "--input", type=str, help="Process a specific folder (album or CD folder).")
    args = parser.parse_args()

    if not any(vars(args).values()):
        # No arguments provided, show usage screen
        parser.print_help()
        sys.exit(1)

    if args.input:
        # Process the specified folder
        if not os.path.isdir(args.input):
            print(f"Error: {args.input} is not a valid directory.")
            sys.exit(1)

        fetch_artwork_for_folder(args.input)
    elif args.all:
        # Process the root music directory
        if not os.path.isdir(ROOT_MUSIC_DIR):
            print(f"Error: {ROOT_MUSIC_DIR} is not a valid directory.")
            sys.exit(1)

        process_folder(ROOT_MUSIC_DIR, process_cd_folders=args.cd)

if __name__ == '__main__':
    main()
