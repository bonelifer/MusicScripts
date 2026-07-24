# Deezer Cover Art Updater

## Description
`deezer-id3tocover.py` walks a music library, reads artist/album from each folder's ID3 tags,
and fetches high-resolution square JPEG artwork from the Deezer API. It only touches folders
that don't already have a cover meeting `MIN_RES`.

## Features
- Queries the public Deezer search API (`api.deezer.com/search/album`) for cover artwork.
- Reads artist/album via `mutagen.easyid3` from the first MP3 with usable tags in each folder.
- Detects `CD`/`Disc`/`Disk` subfolders and processes them alongside the parent album folder.
- Validates downloaded images: must be JPEG/JFIF, square, and at least `MIN_RES` on each side.
- Skips folders that already have a `cover.jpg` meeting `MIN_RES` — logged as "has good cover".
- Graceful Ctrl+C handling — finishes the current folder, then stops.
- `--debug` flag (checked directly against `sys.argv`) for verbose logging.

## Requirements
- **Python 3.x**
- **External libraries**: `mutagen`, `Pillow`, `requests`
- **Configuration file** (`artwork-config.ini`) with:
  - `[paths] rootmusicdir` — root of your music library
  - `[settings] MIN_RES` — minimum acceptable width/height, in pixels (required, no fallback)

## Installation
1. Install Python 3.
2. Install required libraries:
   ```bash
   pip install mutagen pillow requests
   ```
3. Copy `artwork-config.ini.example` to `artwork-config.ini` and set:
   ```ini
   [settings]
   MIN_RES = 500

   [paths]
   rootmusicdir = /media/path/to/your/Music/processing/directory/
   ```

## Usage
```bash
python3 deezer-id3tocover.py            # Process the entire music library
python3 deezer-id3tocover.py --debug    # Same, with verbose debug logging
```

### Command-Line Arguments
| Argument | Description |
|----------|-------------|
| `--debug` | Enable debug-level logging (console and log file). |

There is no `-i`/`-a`/`-c` argument parsing in this script — any other flags are silently
ignored, and it always walks the whole `[paths] rootmusicdir` tree.

## Logging
Logs to `cover_updater.log` in the script's directory, and to the console. Log lines are
timestamped in the file; console lines omit the timestamp. A short plain-`print()` summary
(albums processed, covers updated, log path) is also printed at the end.

## Notes
- Folders with no readable artist/album metadata are skipped (logged at debug level only).
- If no Deezer match is found, the folder is skipped (logged at debug level only).

## License

This project is licensed under the **GNU General Public License v3.0**.

See [LICENSE](../../LICENSE) for more information.
