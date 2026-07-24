# Calculate ReplayGain for MP3 Files

## Description
`calculate_replaygain.sh` applies ReplayGain tags to MP3 files using `mp3gain`. It auto-detects
whether the given path is a single album/CD directory (MP3s directly inside it) or a root
music directory (`ARTIST/ALBUM/[CD]` tree) and processes accordingly.

Two calling contexts are supported:
1. **New-music / single-album**: called with `-p /path/to/one/album` (e.g. from an import
   pipeline) — processes just that directory.
2. **Standalone / full-library**: called with `-p /path/to/root` or no `-p` at all (falls back
   to `rootmusicdir` in `artwork-config.ini`) — traverses the whole tree. For repeated
   full-library runs, prefer [`rg-lib.sh`](README-rg-lib.md), which adds cache-based skipping
   so already-processed albums aren't re-scanned.

## Features
- Auto-detects leaf directory vs. root directory — no separate flag needed.
- Applies album gain (`mp3gain -a -s i -k`) then track gain (`mp3gain -r -s i -k`) per album/CD.
- Supports `ARTIST/ALBUM/CD` and `ARTIST/ALBUM` (no CD subfolder) structures.
- Falls back to `rootmusicdir` from `artwork-config.ini` when `-p` isn't given.

## Requirements
- **Bash**
- **mp3gain**:
  ```bash
  sudo apt install mp3gain      # Debian/Ubuntu
  brew install mp3gain          # macOS (Homebrew)
  ```
- `artwork-config.ini` with `[paths] rootmusicdir`, unless you always pass `-p`.

## Usage
```bash
./calculate_replaygain.sh                          # Uses rootmusicdir from artwork-config.ini
./calculate_replaygain.sh -p /path/to/music         # Full-tree run against an explicit root
./calculate_replaygain.sh -p "/path/to/Artist/Album"  # Single album/CD directory
```

### Command-Line Arguments
| Argument | Description |
|----------|-------------|
| `-p`, `--path` | Directory to process — a leaf album/CD dir, or a root music dir. Overrides `artwork-config.ini`. |
| `-h`, `--help` | Print usage and exit. |

## Notes
- ReplayGain tags are written directly to the MP3 files (`-k` avoids clipping on tagged gain).
- `-s i` skips files that already carry ReplayGain tags matching the target scheme.
- For bulk re-processing of an entire library with cache-based skipping, use
  [`rg-lib.sh`](README-rg-lib.md) instead of calling this script directly.

## License

This project is licensed under the **GNU General Public License v3.0**.

See [LICENSE](../../LICENSE) for more information.
