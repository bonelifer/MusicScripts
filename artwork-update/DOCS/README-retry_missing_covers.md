# Retry Missing Covers

## Description
`retry_missing_covers.sh` regenerates `missing_covers.txt` (by calling
[`find_missing_covers.sh`](README-find_missing_covers.md)), then runs the full
[`run.sh`](README-run.md) pipeline against each listed folder individually, using `-i`/`--input`
(or `-p`/`--path` for the two scripts with no `-i` mode) instead of a whole-library pass. Use
this to retry just the CD folders known to be missing a cover, without re-scanning everything
`run.sh` already covered.

## Features
- Always refreshes `missing_covers.txt` first, so the retry list reflects current state.
- For each folder, runs every script from `run.sh` in the same order: strip embedded art, all
  four artwork sources, resize, compress, clean up backups, the (here always a no-op)
  root-cover-removal step, ReplayGain, and MP3 validation.
- Every step runs for every folder regardless of whether an earlier step succeeded or failed —
  same philosophy as `run.sh` itself: one failure doesn't abort the batch.
- Exits early with a success message if `missing_covers.txt` comes back empty.

## Requirements
Everything required by the individual scripts it calls — see each script's own doc in this
folder. `find_missing_covers.sh` must be present in the same directory.

## Usage
```bash
./retry_missing_covers.sh                          # Uses rootmusicdir from artwork-config.ini
./retry_missing_covers.sh -p /path/to/music         # Overrides rootmusicdir for this run
```

### Command-Line Arguments
| Argument | Description |
|----------|-------------|
| `-p`, `--path` | Passed through to `find_missing_covers.sh`, overriding `rootmusicdir` from `artwork-config.ini` for this run. |
| `-h`, `--help` | Print usage and exit. |

## Notes
- `export-coverart.py` is called once per folder with `-i`, not twice with `-c -a`/`-a` like
  `run.sh` does — the `-c` distinction only matters when filtering during a whole-library walk,
  and is meaningless once the target folder is already known.
- `root_cover_remover.py` only removes `cover.jpg` from album-root folders that have CD
  subfolders, and always skips a path that is itself a CD folder — so its step here is a
  harmless no-op. It's still included, to mirror `run.sh`'s step order exactly.
- `album_cover_reducer_to_1400px.py` and `album_cover_compressor_to_jpg90.py` have no `-i` mode,
  so they're scoped with `-p` instead — this works correctly for a single folder since both
  scripts check every file directly under the given path for one named `cover.jpg`, without
  skipping the path itself (unlike the artwork-fetch scripts' walk logic).
- Re-run `find_missing_covers.sh` afterward to see what's still missing — this script doesn't
  do that automatically, since overwriting `missing_covers.txt` again would lose the list this
  run just processed.

## License

This project is licensed under the **GNU General Public License v3.0**.

See [LICENSE](../../LICENSE) for more information.
