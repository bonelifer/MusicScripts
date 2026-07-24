# Picard Album Processor

## Description
`picard_album_processor.sh` automates batch-processing a music library with MusicBrainz Picard.
It walks `ARTIST/ALBUM/` folders under `music_directory`, sends each album to Picard along with
a fixed sequence of Picard commands (`commands.txt`), then moves the album to `output_directory`
on success or `failed_directory` on failure. Processed and failed albums are tracked in text
files so re-runs skip work already done.

Picard is expected to keep running in the background across the whole session: the script
launches it once if it isn't already running, and each album is sent to that running instance
via `picard -e LOAD <album> -e FROM_FILE commands.txt` rather than spawning a fresh Picard
process per album.

## Features
- Processes every album folder under `music_directory`, one `ARTIST/ALBUM` pair at a time.
- Runs the Picard command sequence in `commands.txt` (cluster, lookup, fingerprint, scan, save,
  then quit) against each album.
- Tracks successes in `processed_albums.txt` and failures in `failed_albums.txt`, both written
  into `music_directory`; already-tracked albums are skipped on the next run.
- Moves successful albums to `output_directory/<Artist>/`, failed albums to
  `failed_directory/<Artist>/`.
- Restarts Picard automatically if it isn't running, checked once per pass.
- Removes an artist folder if it ends up empty after processing.
- Loops until a full pass processes zero new albums, then exits.

## Requirements
- **Bash**
- **MusicBrainz Picard**, installed and on `$PATH`
- `commands.txt` (included) — the Picard command sequence to run per album
- `picard-config.ini` — see below

## Installation
1. Install Picard and confirm it's on `$PATH`:
   ```bash
   picard --version
   ```
2. Copy the example config and fill in your paths:
   ```bash
   cp picard-config.ini.example picard-config.ini
   ```
   ```ini
   [paths]
   music_directory = /media/path/to/your/Music/processing/directory/
   output_directory = /media/path/to/your/Music/processing/directory/Picard/
   ```
3. Make the script executable:
   ```bash
   chmod +x picard_album_processor.sh
   ```

## Usage
Run from within this directory, so the script can find `picard-config.ini` and `commands.txt`:
```bash
./picard_album_processor.sh
```

### Expected library layout
```
music_directory/
├── Artist1/
│   ├── Album1/
│   └── Album2/
└── Artist2/
    └── Album1/
```

## Logging
No `.log` file. Progress is printed to the console. Two plain-text trackers are written into
`music_directory`:
- `processed_albums.txt` — one album path per line, successfully processed
- `failed_albums.txt` — one album path per line, Picard reported failure

Delete an album's line from either file to force it to be reprocessed on the next run.

## Notes
- `failed_directory` defaults to `<music_directory>/Failed` if left unset in
  `picard-config.ini`. That folder is itself excluded from processing on later runs.
- Failed albums are moved out of `music_directory`, not left in place — review
  `failed_directory` and `failed_albums.txt` to see what needs manual attention.
- This script doesn't share `artwork-config.ini` with the scripts in
  [`artwork-update/`](../../artwork-update/) — Picard automation and cover-art fetching are
  different enough workflows that they're kept on separate config files.

## License

This project is licensed under the **GNU General Public License v3.0**.

See [LICENSE](../../LICENSE) for more information.
