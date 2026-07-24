# Album Cover Art Compressor (JPEG quality 90)

## Description
`album_cover_compressor_to_jpg90.py` walks a music library and re-saves any `cover.jpg` that is
1.0 MiB or larger at JPEG quality 90, shrinking file size without changing dimensions. Intended
to run after [`album_cover_reducer_to_1400px.py`](README-album_cover_reducer_to_1400px.md),
since that script controls resolution while this one controls file size.

## Features
- Re-encodes `cover.jpg` files ≥ 1.0 MiB at quality 90 (dimensions unchanged).
- Converts any color mode (RGBA/P/L/etc.) to RGB before saving, since JPEG doesn't support them.
- Verifies the re-encoded output before replacing the original; keeps a `cover.jpg.bak` of the
  pre-compression file.
- `--debug` flag (checked directly against `sys.argv`) for verbose logging.

## Requirements
- **Python 3.x**
- **External library**: `Pillow`
- **Configuration file** (`artwork-config.ini`) with `[paths] rootmusicdir`.

## Installation
1. Install Python 3.
2. Install required library:
   ```bash
   pip install pillow
   ```
3. Copy `artwork-config.ini.example` to `artwork-config.ini` and set `[paths] rootmusicdir`.

## Usage
```bash
python3 album_cover_compressor_to_jpg90.py            # Process the entire music library
python3 album_cover_compressor_to_jpg90.py --debug    # Same, with verbose debug logging
```
No `-i`/`-a` folder selector — it always walks the whole `[paths] rootmusicdir` tree looking
for files literally named `cover.jpg`.

## Logging
Logs to `cover_reducer.log` in the script's directory, and to the console. Log lines are
timestamped in the file; console lines omit the timestamp. A plain-`print()` summary
(processed/reduced/errors/skipped counts, log path) is printed at the end.

## Notes
- Covers under 1.0 MiB are left untouched regardless of dimensions.
- A compression failure leaves the original `cover.jpg` in place — no partial writes.

## License

This project is licensed under the **GNU General Public License v3.0**.

See [LICENSE](../../LICENSE) for more information.
