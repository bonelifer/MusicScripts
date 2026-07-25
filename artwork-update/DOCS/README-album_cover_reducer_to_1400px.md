# Album Cover Art Reducer (resize to 1400px)

## Description
`album_cover_reducer_to_1400px.py` walks a music library and downsizes any `cover.jpg` wider or
taller than 1400px, saving the result back over the original (with a `.bak` backup of the
pre-resize file).

## Features
- Resizes any `cover.jpg` exceeding 1400px on either axis, preserving aspect ratio.
- Handles corrupted images, decompression bombs (400MP pixel cap), unusual color modes
  (RGBA/P/L converted to RGB), permission errors, and non-image files without crashing.
- Verifies the resized output before replacing the original; keeps a `cover.jpg.bak` of the
  pre-resize file.
- `--debug` flag for verbose logging; `-p/--path` to override the music directory for one run.

## Requirements
- **Python 3.x**
- **External library**: `Pillow`
- **Configuration file** (`artwork-config.ini`) with `[paths] rootmusicdir`, unless `-p` is
  always used instead.

## Installation
1. Install Python 3.
2. Install required library:
   ```bash
   pip install pillow
   ```
3. Copy `artwork-config.ini.example` to `artwork-config.ini` and set `[paths] rootmusicdir`.

## Usage
```bash
python3 album_cover_reducer_to_1400px.py                    # Process the entire music library
python3 album_cover_reducer_to_1400px.py --debug            # Same, with verbose debug logging
python3 album_cover_reducer_to_1400px.py -p /path/to/music   # Same, overriding rootmusicdir
```

### Command-Line Arguments
| Argument | Description |
|----------|-------------|
| `--debug` | Enable debug-level logging (console and log file). |
| `-p`, `--path` | Override `[paths] rootmusicdir` from `artwork-config.ini` for this run. |

No `-i`/`-a` folder selector — it always walks the whole configured (or overridden) tree
looking for files literally named `cover.jpg`.

## Logging
Logs to `cover_resizer.log` in the script's directory, and to the console. Log lines are
timestamped in the file; console lines omit the timestamp. A plain-`print()` summary
(processed/resized/errors/skipped counts, log path) is printed at the end.

## Notes
- Covers already at or under 1400px on both axes are left untouched.
- A resize failure leaves the original `cover.jpg` in place — no partial writes.

## License

This project is licensed under the **GNU General Public License v3.0**.

See [LICENSE](../../LICENSE) for more information.
