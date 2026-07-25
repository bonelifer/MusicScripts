#!/usr/bin/bash
#
# run-light.sh
#
# Description:
#   Cover-art-only subset of run.sh: fetches missing/low-res covers from
#   all four artwork sources, resizes and compresses the results, and
#   cleans up leftover backups. Skips run.sh's export-coverart.py step
#   (no embedded-artwork extraction/stripping) and its ReplayGain/
#   mp3validate.sh steps at the end. Use this when you just want fresh
#   cover art without touching embedded MP3 artwork or re-running
#   ReplayGain/validation. See DOCS/README-run.md for how this compares
#   to run.sh step-by-step.
#
# Requirements:
#   - Everything required by the individual scripts called below; see each
#     script's own doc in DOCS/, or run ./install-reqs.sh to install the
#     Python/system package union.
#   - artwork-config.ini set up with [paths] rootmusicdir.
#
# Usage:
#   ./run-light.sh
#
# Notes:
#   - No step's exit code is checked; a failure partway through does not
#     stop the pipeline, matching run.sh's own behavior.
#   - Must be run from inside this directory (artwork-update/), since every
#     call below is a relative path and every script reads
#     ./artwork-config.ini relative to the current directory.
#

# The four artwork sources, in order. Each one only touches folders that
# still need a cover (or a higher-resolution one), so running all four
# unconditionally is safe and idempotent.
python3 ./apple-music-id3tocover.py
echo " "
python3 ./mb-cca-id3tocover.py -a
echo " "
python3 ./deezer-id3tocover.py
echo " "
python3 ./lastfm-id3tocover.py
echo " "

# Shrink any cover.jpg that's still oversized (resolution, then file size)
# after the fetch step above.
python3 ./album_cover_reducer_to_1400px.py
echo " "
python3 ./album_cover_compressor_to_jpg90.py
echo " "

# Keep the smaller of cover.jpg / cover.jpg.bak left behind by the resize
# and compress steps above, discarding the larger one.
python3 ./cleanup_cover_art.py -a
echo " "

# Remove cover.jpg from album-root folders that have CD subfolders, since
# each CD subfolder already carries its own cover and a root-level one is
# redundant. --confirm means this actually deletes files, not a dry run.
python3 ./root_cover_remover.py --confirm
