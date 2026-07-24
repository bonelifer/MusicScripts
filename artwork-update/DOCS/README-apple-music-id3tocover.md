# Apple Music Cover Art Updater

## Description
`apple-music-id3tocover.py` walks a music library, reads artist/album from each folder's ID3
tags, and fetches high-resolution artwork from the Apple Music (iTunes) catalog via `itunespy`.
It adds `cover.jpg` when missing and upgrades it when the fetched image is meaningfully larger
than the existing one.

## Features
- Searches iTunes for the album and requests the `1200x1200` artwork variant.
- Reads artist/album from the first `.mp3` with usable `TPE1`/`TALB` tags in each folder.
- Detects `CD`/`Disc`/`Disk` subfolders and processes them alongside the parent album folder.
- Only replaces an existing cover if the new image has at least 10% more pixels.
- Rejects downloads under 50KB (likely placeholder/broken images) before saving.
- Graceful Ctrl+C handling — finishes the current folder, then stops.
- `-d/--debug` flag for verbose (DEBUG level) logging.

## Requirements
- **Python 3.x**
- **External libraries**: `mutagen`, `Pillow`, `requests`, `itunespy`
- **Configuration file** (`artwork-config.ini`) with:
  - `[paths] rootmusicdir` — root of your music library
  - `[settings] MIN_RES` — optional, defaults to `500` (not currently used to gate downloads,
    kept for config compatibility with the other cover-art scripts)

## Installation
1. Install Python 3.
2. Install required libraries:
   ```bash
   pip install mutagen pillow requests itunespy
   ```
3. Copy `artwork-config.ini.example` to `artwork-config.ini` and set:
   ```ini
   [paths]
   rootmusicdir = /media/path/to/your/Music/processing/directory/
   ```

## Usage
```bash
python3 apple-music-id3tocover.py            # Process the entire music library
python3 apple-music-id3tocover.py -d         # Same, with verbose debug logging
```

### Command-Line Arguments
| Argument | Description |
|----------|-------------|
| `-d`, `--debug` | Enable debug-level logging (console and log file). |

There is no `-i`/`-a` folder selector — the script always walks the whole
`[paths] rootmusicdir` tree.

## Logging
Logs to `apple-music-artwork.log` in the script's directory, and to the console. Log lines are
timestamped in the file; console lines omit the timestamp.

## Notes
- Folders with no readable artist/album metadata are logged and skipped.
- If no iTunes match is found, the folder is logged as `No artwork found` and left untouched.

## License

This project is licensed under the **GNU General Public License v3.0**.

See [LICENSE](../../LICENSE) for more information.
