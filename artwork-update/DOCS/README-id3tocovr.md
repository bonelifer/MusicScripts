# ID3 to Cover Art Fetcher

## Description
This script automates the process of fetching album artwork for music files stored in a specified directory. It supports fetching artwork from multiple sources, including iTunes, MusicBrainz, and Last.fm. The script reads configuration from an INI file and allows for high-resolution artwork fetching. It is designed to handle large music libraries and can process both album folders and CD subfolders.

## Features
- Fetches artwork from iTunes, MusicBrainz (Cover Art Archive), and Last.fm.
- Supports high-resolution artwork fetching with configurable minimum resolution.
- Handles ID3 tags to extract artist and album information.
- Logs all actions and errors for troubleshooting.
- Configurable via an INI file (`artwork-config.ini`).
- Processes entire music libraries or specific folders.
- Supports CD subfolders (e.g., CD 1, CD 2) for multi-disc albums.

## Requirements
- **Python 3.x**: The script is written in Python 3 and requires a compatible version.
- **External Libraries**:
  - `mutagen`: For reading ID3 tags in MP3 files.
  - `itunespy`: For fetching artwork from iTunes.
  - `musicbrainzngs`: For fetching release IDs and artwork from MusicBrainz.
  - `pylast`: For fetching artwork from Last.fm.
  - `requests`: For downloading artwork from URLs.
  - `pillow`: For image processing (resizing and format conversion).
- **Configuration File**: A configuration file (`artwork-config.ini`) with the following fields:
  - `rootmusicdir`: The root directory of your music library.
  - `useragent_email`: Your email for MusicBrainz API usage.
  - `lastfm-apikey`: Your Last.fm API key.
  - `USE_HIRES`, `MIN_RES`, `USE_FALLBACK`, `USE_HIRES_PRIORITY`, `USE_MUSICBRAINZ`, `NO_LOW_RES`: Settings for artwork fetching behavior.

## Installation
1. **Install Python 3.x**: Ensure Python 3 is installed on your system. You can download it from [python.org](https://www.python.org/).
2. **Install Required Libraries**:
   ```bash
   pip install mutagen itunespy musicbrainzngs pylast requests pillow
   ```
3. **Set Up Configuration File**:
   Rename the file `artwork-config.ini.example` to `artwork-config.ini` in the same directory as the script and adjust the following content:
   ```ini
   [musicbrainz]
   useragent_email = your.email@example.com

   [credentials]
   lastfm-apikey = your_lastfm_api_key

   [settings]
   USE_HIRES = True
   MIN_RES = 600
   USE_FALLBACK = True
   USE_HIRES_PRIORITY = True
   USE_MUSICBRAINZ = True
   NO_LOW_RES = False

   [paths]
   rootmusicdir = /path/to/your/music/library
   ```
   Replace the placeholders with your actual email, Last.fm API key, and music library path.

## Usage
The script can be run with the following command-line arguments:

### Examples
1. **Process a Specific Folder**:
   ```bash
   python3 id3tocovr.py -i "/path/to/album/folder/"
   ```
   This will fetch and save cover art for the specified folder.

2. **Process the Entire Music Library**:
   ```bash
   python3 id3tocovr.py -a
   ```
   This will recursively process all folders in the root music directory.

3. **Process Only CD Folders**:
   ```bash
   python3 id3tocovr.py -a -c
   ```
   This will process only folders named `CD 1`, `CD 2`, etc., within the music library.

### Command-Line Arguments
| Argument | Description |
|----------|-------------|
| `-i`, `--input` | Process a specific folder (album or CD folder). |
| `-a`, `--all`   | Process the entire music library. |
| `-c`, `--cd`    | Process only CD folders (e.g., CD 1, CD 2). |

## Logging
The script logs its actions and errors to a file named `album-artwork.log` in the same directory as the script. This log file can be used for troubleshooting.

## Notes
- The script skips folders where `cover.jpg` already exists.
- If no artwork is found, the script logs a warning and moves to the next folder.
- High-resolution artwork is prioritized if `USE_HIRES_PRIORITY` is enabled.

## License

This project is licensed under the **GNU General Public License v3.0**.

See [LICENSE](../../LICENSE) for more information.
