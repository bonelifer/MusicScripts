# Changelog

All notable changes to this project are documented here.

## Initial Release — 2025-03-23 to 2026-07-25

### ✨ Features

- **artwork-update**: Fetches album cover art from four different sources, resizes and compresses it, cleans up backups and redundant copies, applies ReplayGain, and validates MP3s.
- **picard_album_processor**: Batch-runs MusicBrainz Picard across your library, tracking successes/failures and restarting Picard automatically as needed. It now has its own config file and dedicated documentation.
- **One-time setup script**: `install-reqs.sh` installs all dependencies for `artwork-update` in one step, and `run.sh`/`run-light.sh` are now fully documented inline.
- **Missing-cover detection**: New tooling to find albums missing cover art, with scan target/result counts printed as it runs.
- **Per-source artwork scripts**: `id3tocovr.py` was split into separate scripts per artwork source for easier maintenance; the old `embed-artwork.py` was retired.
- **Manual path overrides**: Added `-p`/`-i` override flags across the artwork-update scripts for specifying paths directly.

### 🔧 Improvements

- Renamed `rg-lib.sh` to `replaygain-library.sh` for clarity.
- Rewrote the root README and both sub-project docs for clarity, with a full script/purpose table and links to the wiki configuration pages.

## Links

- [GitHub Repository](https://github.com/bonelifer/MusicScripts)
