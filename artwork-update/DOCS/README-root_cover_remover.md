# Remove Cover Art from Album Root Folders

## Description
`root_cover_remover.py` removes `cover.jpg` from album root folders that have CD subfolders,
since in that layout each CD subfolder carries its own cover and a root-level `cover.jpg` is
redundant clutter. CD subfolder covers are always preserved. Runs as a dry run by default.

## Features
- Walks the whole music library looking for `cover.jpg` files.
- Skips any folder identified as a CD subfolder (name starts with `cd `/`disc `, or contains
  `cd`/`disc`/`disk` anywhere in the name).
- Deletes `cover.jpg` in every other folder that has one — including artist- and label-level
  folders, not just album roots, since the check is name-based rather than structure-based.
- Dry-run by default; `--confirm` is required to actually delete anything.

## Requirements
- **Python 3.x** (standard library only — no extra packages)
- **Configuration file** (`artwork-config.ini`) with `[paths] rootmusicdir`.

## Installation
1. Install Python 3.
2. Copy `artwork-config.ini.example` to `artwork-config.ini` and set `[paths] rootmusicdir`.

## Usage
```bash
python3 root_cover_remover.py              # Dry run — lists what would be removed
python3 root_cover_remover.py --confirm    # Actually deletes the files
```

### Command-Line Arguments
| Argument | Description |
|----------|-------------|
| `--confirm` | Actually perform deletions. Without it, the script only logs what it would do. |

## Logging
Logs to `cover-cleanup.log` in the script's directory, and to the console. Log lines are
timestamped in the file; console lines omit the timestamp.

## Notes
- **Always run without `--confirm` first** and review the log — the CD-subfolder detection is
  a substring match on the folder name, so a folder like `Disco Classics` would be (correctly,
  if coincidentally) treated as a CD subfolder and skipped, while intent should be verified for
  your own library's naming.
- This script shares its default log filename (`cover-cleanup.log`) with `cleanup_cover_art.py`'s
  log (`cover_cleanup.log`) only by near-coincidence of naming — they are two different files.

## License

This project is licensed under the **GNU General Public License v3.0**.

See [LICENSE](../../LICENSE) for more information.
