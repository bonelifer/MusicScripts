# ReplayGain Full-Library Cache Wrapper

## Description
`replaygain-library.sh` is a cache-aware wrapper around [`calculate_replaygain.sh`](README-calculate_replaygain.md)
for full-library ReplayGain processing. It discovers every album (and CD subfolder) directory
containing MP3s under a root music path and runs `calculate_replaygain.sh -p` on each one,
skipping any directory already recorded in a local cache file. Use `calculate_replaygain.sh`
directly for a single newly-imported album; use `replaygain-library.sh` for (re-)processing the whole
library efficiently.

## Features
- Finds every unique directory containing MP3 files under the root (one entry per CD
  subdirectory for multi-disc albums, matching how `calculate_replaygain.sh` processes them).
- Tracks completed albums in `~/.replaygain_cache.txt`; already-cached albums are skipped on
  subsequent runs unless `--force` is given.
- `--clear-cache` wipes the cache before processing.
- `--debug` enables `bash -x` trace output.
- Prints a processed/skipped/failed summary at the end and exits non-zero if any album failed.

## Requirements
- **Bash**, `find`, `grep`
- `calculate_replaygain.sh` present in the same directory (auto-`chmod +x`'d if needed)
- `artwork-config.ini` with `[paths] rootmusicdir`, unless you always pass `-p`

## Usage
```bash
./replaygain-library.sh                              # Full run against rootmusicdir from artwork-config.ini
./replaygain-library.sh -p /path/to/music            # Full run against an explicit root
./replaygain-library.sh --force                      # Re-process albums even if cached
./replaygain-library.sh --clear-cache                # Wipe the cache, then run
```

### Command-Line Arguments
| Argument | Description |
|----------|-------------|
| `-p`, `--path` | Base music directory (overrides `artwork-config.ini`). |
| `--clear-cache` | Wipe the cache file before processing. |
| `--force`, `-f` | Re-process albums even if already cached. |
| `--debug` | Enable `bash -x` trace output. |
| `-h`, `--help` | Print usage and exit. |

## Notes
- The cache file (`~/.replaygain_cache.txt`) is a plain list of processed album directory
  paths, one per line — safe to inspect or hand-edit.
- A per-album failure is reported but doesn't stop the run; the script exits `1` at the end if
  any album failed.

## License

This project is licensed under the **GNU General Public License v3.0**.

See [LICENSE](../../LICENSE) for more information.
