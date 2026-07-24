# artwork-update

A collection of Python and Bash scripts for maintaining album cover art and audio quality
metadata across an `ARTIST/ALBUM/[CD]`-structured MP3 library: fetching missing/low-res cover
art from multiple sources, resizing and compressing existing covers, cleaning up leftover
backup files, and calculating ReplayGain.

All scripts share a single config file, `artwork-config.ini`, and (with a couple of noted
exceptions) log to both the console and a per-script `.log` file in this directory.

## Quick start

1. Install the dependencies each script needs — see the individual doc in [`DOCS/`](DOCS/) for
   exact `pip install` / `apt install` commands.
2. Copy the example config and fill in your values:
   ```bash
   cp artwork-config.ini.example artwork-config.ini
   ```
   ```ini
   [musicbrainz]
   useragent_email = yourname@gmail.com

   [lastfm]
   API_KEY = your_lastfm_api_key

   [settings]
   MIN_RES = 500

   [paths]
   rootmusicdir = /path/to/your/Music/
   ```
3. Run scripts individually as needed, or run the full pipeline:
   ```bash
   ./run.sh          # full pipeline: artwork fetch + resize/compress + ReplayGain + validation
   ./run-light.sh     # cover-art-only pipeline, no ReplayGain/validation
   ```
   See [`DOCS/README-run.md`](DOCS/README-run.md) for exactly what each wrapper runs and in
   what order.

## Scripts

### Cover art — fetch
| Script | Source | Doc |
|---|---|---|
| `mb-cca-id3tocover.py` | MusicBrainz Cover Art Archive | [DOCS/README-mb-cca-id3tocover.md](DOCS/README-mb-cca-id3tocover.md) |
| `apple-music-id3tocover.py` | Apple Music / iTunes | [DOCS/README-apple-music-id3tocover.md](DOCS/README-apple-music-id3tocover.md) |
| `deezer-id3tocover.py` | Deezer | [DOCS/README-deezer-id3tocover.md](DOCS/README-deezer-id3tocover.md) |
| `lastfm-id3tocover.py` | Last.fm | [DOCS/README-lastfm-id3tocover.md](DOCS/README-lastfm-id3tocover.md) |
| `export-coverart.py` | Embedded MP3 artwork (extracts, then strips it) | [DOCS/README-export-coverart.md](DOCS/README-export-coverart.md) |

### Cover art — maintain
| Script | Purpose | Doc |
|---|---|---|
| `album_cover_reducer_to_1400px.py` | Downsize covers over 1400px | [DOCS/README-album_cover_reducer_to_1400px.md](DOCS/README-album_cover_reducer_to_1400px.md) |
| `album_cover_compressor_to_jpg90.py` | Recompress covers ≥ 1.0 MiB at quality 90 | [DOCS/README-album_cover_compressor_to_jpg90.md](DOCS/README-album_cover_compressor_to_jpg90.md) |
| `cleanup_cover_art.py` | Keep the smaller of `cover.jpg` / `cover.jpg.bak` | [DOCS/README-cleanup_cover_art.md](DOCS/README-cleanup_cover_art.md) |
| `root_cover_remover.py` | Remove redundant `cover.jpg` from multi-disc album roots | [DOCS/README-root_cover_remover.md](DOCS/README-root_cover_remover.md) |

### Audio quality
| Script | Purpose | Doc |
|---|---|---|
| `calculate_replaygain.sh` | Apply ReplayGain tags (single album or full library) | [DOCS/README-calculate_replaygain.md](DOCS/README-calculate_replaygain.md) |
| `rg-lib.sh` | Cache-aware full-library wrapper around `calculate_replaygain.sh` | [DOCS/README-rg-lib.md](DOCS/README-rg-lib.md) |
| `mp3validate.sh` | Validate/fix MP3 files with `mp3val` | [DOCS/README-mp3validate.md](DOCS/README-mp3validate.md) |

### Orchestration
| Script | Purpose | Doc |
|---|---|---|
| `run.sh` | Full pipeline (all of the above, in order) | [DOCS/README-run.md](DOCS/README-run.md) |
| `run-light.sh` | Cover-art-only pipeline | [DOCS/README-run.md](DOCS/README-run.md) |

### Configuration
| File | Purpose |
|---|---|
| `artwork-config.ini.example` | Template — copy to `artwork-config.ini` and fill in |
| `artwork-config.ini` | Your actual config (git-ignored; contains API keys) |

`artists.txt` and `lidarr-import-config.ini` are not read by any script currently in this
directory — they appear to be leftovers from a removed Lidarr-import workflow. Safe to ignore
or remove unless you're reviving that workflow.

## License

This project is licensed under the **GNU General Public License v3.0**.

See [LICENSE](../LICENSE) for more information.
