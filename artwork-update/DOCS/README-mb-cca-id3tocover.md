# MusicBrainz Cover Art Archive Fetcher

## Description
`mb-cca-id3tocover.py` scans a music library for album folders, reads the artist/album from
the first MP3's ID3 tags, and looks up matching artwork on the MusicBrainz Cover Art Archive.
It adds `cover.jpg` when missing, or replaces it when the fetched image is larger than the
existing one or the existing one doesn't meet the configured minimum resolution.

## Features
- Looks up releases via the MusicBrainz search API and fetches the release's front cover image.
- Reads artist/album from the first `.mp3` file's ID3 tags (`TPE1`, `TALB`) in each folder.
- Detects `CD 1`, `CD 2`, ... subfolders and processes each disc independently.
- Adds `cover.jpg` if missing, replaces it only if the new image is larger or the existing one
  is below `MIN_RES`, otherwise keeps the existing cover.
- Validates downloaded images (verifies they open correctly) before replacing anything.
- Logs a one-line result per album: `↑ added`, `↑ replaced`, `✓ kept existing`, or `✗ no artwork found`.

## Requirements
- **Python 3.x**
- **External libraries**: `mutagen`, `musicbrainzngs`, `requests`, `Pillow`
- **Configuration file** (`artwork-config.ini`) with:
  - `[settings] MIN_RES` — minimum acceptable width/height, in pixels
  - `[paths] rootmusicdir` — root of your music library

## Installation
1. Install Python 3.
2. Install required libraries:
   ```bash
   pip install mutagen musicbrainzngs requests pillow
   ```
3. Copy `artwork-config.ini.example` to `artwork-config.ini` and set at least:
   ```ini
   [settings]
   MIN_RES = 500

   [paths]
   rootmusicdir = /media/path/to/your/Music/processing/directory/
   ```
   The script exits with an error at startup if `[settings] MIN_RES` or `[paths] rootmusicdir`
   is missing.

## Usage
```bash
python3 mb-cca-id3tocover.py -i "/path/to/album/folder/"   # Process a specific folder
python3 mb-cca-id3tocover.py -a                             # Process the entire music library
```

### Command-Line Arguments
| Argument | Description |
|----------|-------------|
| `-i`, `--input` | Process a specific folder (album or CD folder). |
| `-a`, `--all`   | Process the entire music library (`rootmusicdir` from config). |

One of `-i` or `-a` is required.

## Logging
Logs to `mb-cca-artwork.log` in the script's directory, and to the console. Log lines are
timestamped in the file (`timestamp - LEVEL - message`); console lines omit the timestamp
(`LEVEL - message`).

## Notes
- Folders with no `.mp3` files are skipped with a warning.
- If MusicBrainz has no release match or no front cover image, the album is logged as
  `no artwork found` and left untouched.

## License

This project is licensed under the **GNU General Public License v3.0**.

See [LICENSE](../../LICENSE) for more information.
