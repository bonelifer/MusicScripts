# Find Missing Covers (CD subfolders with no cover.jpg)

## Description
`find_missing_covers.sh` scans a music library for multi-disc `CD N` subfolders and reports
every one that has no `cover.jpg` directly inside it. It's a discovery/reporting tool, not a
fetcher. Use it to find gaps the artwork-fetch scripts haven't filled yet, or to spot-check
after a run.

## Features
- Finds every directory named `CD <something>` anywhere under the music directory.
- For each one, checks for a `cover.jpg` (case-insensitive) directly inside it — no recursion
  into further subfolders.
- Writes the folders missing a cover to `missing_covers.txt`, one path per line.
- Top-level album folders without a `CD N` subfolder are not checked at all. This script is
  scoped to multi-disc albums only.

## Requirements
- **Bash**, `find`
- `artwork-config.ini` with `[paths] rootmusicdir`, unless `-p` is always used instead

## Installation
1. Copy `artwork-config.ini.example` to `artwork-config.ini` and set `[paths] rootmusicdir`
   (skip this if you'll always use `-p`).

## Usage
```bash
./find_missing_covers.sh                          # Uses rootmusicdir from artwork-config.ini
./find_missing_covers.sh -p /path/to/music         # Overrides rootmusicdir for this run
```

### Command-Line Arguments
| Argument | Description |
|----------|-------------|
| `-p`, `--path` | Directory to scan. Overrides `rootmusicdir` from `artwork-config.ini` for this run. |
| `-h`, `--help` | Print usage and exit. |

## Output
Writes one folder path per line to `missing_covers.txt` in the current directory (git-ignored,
since it's a per-run report rather than project source). Any existing `missing_covers.txt` is
overwritten. An empty file means no `CD N` subfolder is missing a cover.

## Notes
- This only checks `CD N` subfolders, not top-level album folders. An album with no `CD`
  subfolder structure at all won't be checked or reported, even if it has no cover.
- Every artwork-fetch script in this directory now supports `-i <folder>` to process a single
  folder directly. [`retry_missing_covers.sh`](README-retry_missing_covers.md) does exactly
  that — it calls this script, then retries the full pipeline against each folder it lists.

## License

This project is licensed under the **GNU General Public License v3.0**.

See [LICENSE](../../LICENSE) for more information.
