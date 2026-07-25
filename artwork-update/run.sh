#!/usr/bin/bash
#
# run.sh
#
# Description:
#   Full pipeline: strips and re-derives embedded MP3 cover art, fetches
#   missing/low-res covers from all four artwork sources, resizes and
#   compresses the results, cleans up leftover backups and redundant
#   covers, then applies ReplayGain and validates every MP3. Runs each
#   step against the whole library (rootmusicdir from artwork-config.ini);
#   none of these calls pass -p, so edit this file directly to scope a run
#   to a different directory. See DOCS/README-run.md for the full step
#   list and DOCS/README-retry_missing_covers.md for a targeted-retry
#   alternative that doesn't require editing anything.
#
# Requirements:
#   - Everything required by the individual scripts called below; see each
#     script's own doc in DOCS/, or run ./install-reqs.sh to install the
#     Python/system package union.
#   - artwork-config.ini set up with [paths] rootmusicdir.
#
# Usage:
#   ./run.sh
#
# Notes:
#   - No step's exit code is checked; a failure partway through does not
#     stop the pipeline. This is deliberate, matching how each individual
#     script is itself designed to skip folders it can't handle rather
#     than abort — see the "Notes" section of DOCS/README-run.md.
#   - Must be run from inside this directory (artwork-update/), since every
#     call below is a relative path and every script reads
#     ./artwork-config.ini relative to the current directory.
#

# Extract embedded cover art from MP3s into cover.jpg, then strip it from
# the MP3s. Run twice: first scoped to CD-numbered subfolders only (-c -a),
# then across the whole library (-a) to also catch albums with no CD
# subfolder structure.
python3 ./export-coverart.py -c -a
python3 ./export-coverart.py -a

echo " "

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
echo " "

# Was used to tell the downloader to clear finished items once artwork
# processing was done. Left here commented out as a reminder of the
# intended integration point; re-enable if that endpoint is back in use.
#curl -X POST http://192.168.1.80:6595/api/removeFinishedDownloads

# Apply ReplayGain tags across the whole library, then validate/repair
# every MP3 with mp3val.
bash ./calculate_replaygain.sh
echo " "
bash ./mp3validate.sh
