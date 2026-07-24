# Cover Art Cleanup (keep the smaller of cover.jpg / cover.jpg.bak)

## Description
`cleanup_cover_art.py` looks for album folders that have both `cover.jpg` and a
`cover.jpg.bak` (left behind by [`album_cover_reducer_to_1400px.py`](README-album_cover_reducer_to_1400px.md)
or [`album_cover_compressor_to_jpg90.py`](README-album_cover_compressor_to_jpg90.md)) and keeps
whichever of the two is smaller on disk, deleting the other.

## Features
- Scans for folders containing both `cover.jpg` and `cover.jpg.bak`.
- Keeps the smaller file by byte size; deletes the larger one.
- Supports a specific folder or the entire library.

## Requirements
- **Python 3.x** (standard library only — no extra packages)
- **Configuration file** (`artwork-config.ini`) with `[paths] rootmusicdir`.

## Installation
1. Install Python 3.
2. Copy `artwork-config.ini.example` to `artwork-config.ini` and set `[paths] rootmusicdir`.

## Usage
```bash
python3 cleanup_cover_art.py -i "/path/to/album/folder/"   # Process a specific folder
python3 cleanup_cover_art.py -a                             # Process the entire music library
```

### Command-Line Arguments
| Argument | Description |
|----------|-------------|
| `-i`, `--input` | Process a specific folder. |
| `-a`, `--all`   | Process the entire music library. |

One of `-i` or `-a` is required.

## Logging
Logs to `cover_cleanup.log` in the script's directory, and to the console. Log lines are
timestamped in the file; console lines omit the timestamp.

## Notes
- With `-a`, a folder is only checked if it contains at least one `.mp3` file directly inside
  it.
- If only one of `cover.jpg` / `cover.jpg.bak` exists, the folder is left untouched.

## License

This project is licensed under the **GNU General Public License v3.0**.

See [LICENSE](../../LICENSE) for more information.
