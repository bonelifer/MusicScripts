# Export Cover Art from MP3 Files

## Description
`export-coverart.py` pulls embedded album art out of MP3 files and keeps the
highest-resolution version as `cover.jpg` on disk. **It then strips all embedded artwork from
every MP3 file in the folder**, regardless of whether that MP3's artwork was kept or discarded.
Run this as a one-time "externalize the artwork" step, not as a repeatable cover-art updater —
after the first run there is no embedded artwork left to compare against.

## Features
- Scans every `.mp3` in a folder for embedded `APIC` (cover art) frames and keeps the one with
  the highest pixel count.
- Compares that against any existing `cover.jpg` and writes the higher-resolution one to disk.
- Removes all embedded `APIC` frames from every MP3 in the folder after the comparison,
  regardless of outcome.
- Supports a specific folder, the entire library, or CD-numbered subfolders only.

## Requirements
- **Python 3.x**
- **External libraries**: `mutagen`, `Pillow`
- **Configuration file** (`artwork-config.ini`) with:
  - `[paths] rootmusicdir` — root of your music library (falls back to a hardcoded default
    path if the config or key is missing — set it explicitly to avoid surprises)

## Installation
1. Install Python 3.
2. Install required libraries:
   ```bash
   pip install mutagen pillow
   ```
3. Copy `artwork-config.ini.example` to `artwork-config.ini` and set:
   ```ini
   [paths]
   rootmusicdir = /media/path/to/your/Music/processing/directory/
   ```

## Usage
```bash
python3 export-coverart.py -i "/path/to/album/folder/"   # Process a specific folder
python3 export-coverart.py -a                             # Process the entire music library
python3 export-coverart.py -a -c                          # Process CD-numbered folders only
```
Running with no arguments prints help and exits.

### Command-Line Arguments
| Argument | Description |
|----------|-------------|
| `-i`, `--input` | Process a specific folder (album or CD folder). |
| `-a`, `--all`   | Process the entire music library. |
| `-c`, `--cd`    | With `-a`, restrict to folders whose name starts with `cd `. |

## Logging
This script does **not** use the `logging` module — all output is `print()` to the console
only. There is no log file.

## Notes
- With `-a` (no `-c`), the script processes *every* directory under `rootmusicdir`, not just
  album-level folders — each one is checked independently for MP3s.
- Folders with no MP3 files are skipped with a printed message.
- Non-JPEG embedded artwork is written to `cover.jpg` as-is (no format conversion).

## License

This project is licensed under the **GNU General Public License v3.0**.

See [LICENSE](../../LICENSE) for more information.
