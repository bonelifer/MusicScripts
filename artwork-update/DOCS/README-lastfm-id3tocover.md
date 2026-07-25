# Last.fm Cover Art Updater

## Description
`lastfm-id3tocover.py` walks a music library, reads artist/album from each folder's ID3 tags,
and adds cover art fetched from the Last.fm `album.getinfo` API for folders that don't already
have any cover image.

## Features
- Queries the Last.fm API for the album's largest listed artwork image.
- Reads artist/album from the first MP3 with usable `TPE1`/`TALB` tags in each folder.
- Skips folders that already have a `cover.jpg` — logged as "has cover" (no resolution check,
  unlike the Deezer/MusicBrainz scripts).
- Graceful Ctrl+C handling — finishes the current folder, then stops.
- `--debug` flag for verbose logging; `-p/--path` to override the music directory for one run;
  `-i/--input` to process a single folder directly.

## Requirements
- **Python 3.x**
- **External libraries**: `mutagen`, `requests`
- **Configuration file** (`artwork-config.ini`) with:
  - `[paths] rootmusicdir` — root of your music library, unless `-p`/`-i` is always used instead
  - `[lastfm] API_KEY` — your Last.fm API key (required even in `-i` mode)

## Installation
1. Install Python 3.
2. Install required libraries:
   ```bash
   pip install mutagen requests
   ```
3. Copy `artwork-config.ini.example` to `artwork-config.ini` and set:
   ```ini
   [lastfm]
   API_KEY = your_lastfm_api_key

   [paths]
   rootmusicdir = /media/path/to/your/Music/processing/directory/
   ```

## Usage
```bash
python3 lastfm-id3tocover.py                            # Process the entire music library
python3 lastfm-id3tocover.py --debug                    # Same, with verbose debug logging
python3 lastfm-id3tocover.py -p /path/to/music           # Same, overriding rootmusicdir
python3 lastfm-id3tocover.py -i "/path/to/album/folder/" # Process a specific folder only
```

### Command-Line Arguments
| Argument | Description |
|----------|-------------|
| `--debug` | Enable debug-level logging (console and log file). |
| `-p`, `--path` | Override `[paths] rootmusicdir` from `artwork-config.ini` for this run. |
| `-i`, `--input` | Process a specific folder (album or CD folder) directly, ignoring `rootmusicdir`/`-p` entirely. |

There is no `-a` flag — omitting `-i` always walks the whole configured (or `-p`-overridden)
tree.

## Logging
Logs to `lastfm_cover_updater.log` in the script's directory, and to the console. Log lines are
timestamped in the file; console lines omit the timestamp. A short plain-`print()` summary
(albums processed, covers added, log path) is also printed at the end.

## Notes
- Folders with no readable artist/album metadata are skipped (logged at debug level only).
- Because there's no resolution check, this script won't upgrade a low-resolution existing
  cover — it only fills in albums that have none. Run `mb-cca-id3tocover.py` or
  `deezer-id3tocover.py` first/after if you also want resolution-based upgrades.

## License

This project is licensed under the **GNU General Public License v3.0**.

See [LICENSE](../../LICENSE) for more information.
