# Embed and Check Artwork Resolution in Music Files

## Description
This script automates the process of embedding and checking the resolution of album cover art in MP3 files. It ensures that the embedded artwork meets a specified resolution (`TEMP_RES`) and resizes the artwork if necessary. The script can process a specific folder, an entire music library, or only CD folders (e.g., CD 1, CD 2).

## Features
- Checks the resolution of existing cover art (`cover.jpg`) in folders.
- Resizes cover art to a specified resolution (`TEMP_RES`) if it exceeds the limit.
- Converts non-JPEG images to JPEG format.
- Embeds resized or original cover art into MP3 files.
- Removes existing embedded artwork if it has a lower resolution than the new artwork.
- Processes specific folders, entire music libraries, or only CD folders.

## Requirements
- **Python 3.x**: The script is written in Python 3 and requires a compatible version.
- **External Libraries**:
  - `mutagen`: For reading and writing ID3 tags in MP3 files.
  - `pillow`: For image processing (resizing and format conversion).
- **Configuration File**: A configuration file (`artwork-config.ini`) with the following fields:
  - `rootmusicdir`: The root directory of your music library.
  - `TEMP_RES`: The desired resolution for resized cover art (optional, default is 600).

## Installation
1. **Install Python 3.x**: Ensure Python 3 is installed on your system. You can download it from [python.org](https://www.python.org/).
2. **Install Required Libraries**:
   ```bash
   pip install mutagen pillow
   ```
3. **Set Up Configuration File**:
   Rename the file `artwork-config.ini.example` to `artwork-config.ini` in the same directory as the script and adjust the following content:
   ```ini
   [paths]
   rootmusicdir = /media/path/to/your/Music/processing/directory/

   [cover_art_script]
   TEMP_RES = 600
   ```
   Replace `/media/path/to/your/Music/processing/directory/` with the actual path to your music library.

## Usage
The script can be run with the following command-line arguments:

### Examples
1. **Process a Specific Folder**:
   ```bash
   python3 embed-artwork.py -i "/path/to/album/folder/"
   ```
   This will embed cover art into MP3 files in the specified folder.

2. **Process the Entire Music Library**:
   ```bash
   python3 embed-artwork.py -a
   ```
   This will recursively process all folders in the root music directory.

3. **Process Only CD Folders**:
   ```bash
   python3 embed-artwork.py -a -c
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
- The script skips folders where `cover.jpg` already exists and meets the resolution requirements.
- If the cover art in an MP3 file has a higher resolution than the new artwork, the script will skip embedding the new artwork.
- Non-JPEG images are automatically converted to JPEG format.

## License

This project is licensed under the **GNU General Public License v3.0**.

See [LICENSE](../../LICENSE) for more information.
