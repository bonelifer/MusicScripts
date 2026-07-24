# Full Pipeline Runners (run.sh / run-light.sh)

## Description
Two orchestration scripts that chain the other scripts in this project into a single
end-to-end music library maintenance pass. Neither takes arguments — edit the script itself to
change the pipeline. Both assume they're run from inside the `artwork-update` directory (they
invoke everything as `./script.py`).

- **`run.sh`** — the full pipeline: export/strip embedded art, fetch from all four artwork
  sources, resize, compress, clean up backups, remove redundant root covers, calculate
  ReplayGain, and validate MP3s.
- **`run-light.sh`** — the same pipeline minus the `export-coverart.py` step and the
  ReplayGain/`mp3validate.sh` steps at the end. Use this when you just want fresh/upgraded
  cover art without touching embedded artwork or re-running ReplayGain/validation.

## Pipeline order

`run.sh`:
1. `export-coverart.py -c -a` — externalize + strip embedded art, CD folders only
2. `export-coverart.py -a` — same, entire library
3. `apple-music-id3tocover.py`
4. `mb-cca-id3tocover.py -a`
5. `deezer-id3tocover.py -c -a` (note: this script ignores all CLI flags — see
   [README-deezer-id3tocover.md](README-deezer-id3tocover.md))
6. `lastfm-id3tocover.py -a` (note: this script also ignores all CLI flags — see
   [README-lastfm-id3tocover.md](README-lastfm-id3tocover.md))
7. `album_cover_reducer_to_1400px.py`
8. `album_cover_compressor_to_jpg90.py`
9. `cleanup_cover_art.py -a`
10. `root_cover_remover.py --confirm`
11. `calculate_replaygain.sh`
12. `mp3validate.sh`

`run-light.sh`: steps 3–10 only (no export-coverart, no ReplayGain, no mp3validate).

## Requirements
Everything required by the individual scripts it calls — see each script's own doc in this
folder. All dependencies (Python packages, `mp3gain`, `mp3val`) must be installed, and
`artwork-config.ini` must be set up, before running either wrapper.

## Usage
```bash
./run.sh          # Full pipeline
./run-light.sh     # Cover-art-only pipeline (no export, ReplayGain, or validation)
```

## Notes
- `root_cover_remover.py --confirm` runs non-interactively and deletes files — make sure
  you're comfortable with what it will remove (see
  [README-root_cover_remover.md](README-root_cover_remover.md)) before running either wrapper
  unattended.
- Because `deezer-id3tocover.py` and `lastfm-id3tocover.py` ignore the `-c`/`-a` flags passed to
  them here, those flags in the pipeline have no effect on those two steps — they always
  process the entire library.
- Neither wrapper checks the exit code of individual steps; a failure partway through does not
  stop the pipeline.

## License

This project is licensed under the **GNU General Public License v3.0**.

See [LICENSE](../../LICENSE) for more information.
