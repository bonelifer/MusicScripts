#!/usr/bin/bash
#
# retry_missing_covers.sh
#
# Description:
#   Regenerates missing_covers.txt (via find_missing_covers.sh), then, for
#   each "CD N" folder it lists, runs every script from run.sh against that
#   one folder using -i/--input (or -p/--path for the two scripts that have
#   no -i mode) instead of the whole library. This lets you retry just the
#   albums known to be missing a cover, in the same order run.sh uses,
#   without a full library pass.
#
#   Every step runs for every folder regardless of whether an earlier step
#   succeeded or failed, matching run.sh's own philosophy (see its header
#   comment / DOCS/README-run.md): a single failure shouldn't abort the
#   whole batch.
#
# Requirements:
#   - Everything required by the individual scripts this calls; see each
#     script's own doc in DOCS/.
#   - find_missing_covers.sh in the same directory.
#
# Usage:
#   ./retry_missing_covers.sh [-p|--path /path/to/music]
#
# Options:
#   -p, --path   Passed through to find_missing_covers.sh, overriding
#                rootmusicdir from artwork-config.ini for this run.
#

readonly MISSING_FILE="missing_covers.txt"

# ----------------------------------------------------------------------------
# Argument parsing (passed straight through to find_missing_covers.sh)
# ----------------------------------------------------------------------------

path_override=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -p|--path)
            path_override="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [-p|--path /path/to/music]"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            echo "Usage: $0 [-p|--path /path/to/music]" >&2
            exit 1
            ;;
    esac
done

# ----------------------------------------------------------------------------
# Step 1: regenerate missing_covers.txt so this run reflects current state,
# not a stale list from an earlier scan.
# ----------------------------------------------------------------------------

echo "🔍 Refreshing $MISSING_FILE..."
if [[ -n "$path_override" ]]; then
    bash ./find_missing_covers.sh -p "$path_override"
else
    bash ./find_missing_covers.sh
fi

if [[ ! -s "$MISSING_FILE" ]]; then
    echo "✅ No missing covers found. Nothing to retry."
    exit 0
fi

total=$(wc -l < "$MISSING_FILE")
echo "📋 $total folder(s) to retry"
echo

# ----------------------------------------------------------------------------
# Step 2: run the full run.sh pipeline against each folder individually.
# ----------------------------------------------------------------------------

n=0
while IFS= read -r dir; do
    [[ -z "$dir" ]] && continue
    n=$((n + 1))
    echo "=========================================="
    echo "🎵 ($n/$total) $dir"
    echo "=========================================="

    # Pull embedded artwork out of this folder's MP3s, if any, before trying
    # external sources. -c/-a from run.sh's two export-coverart.py calls
    # collapse into one -i call here, since -c only matters when filtering
    # during a whole-library walk.
    python3 ./export-coverart.py -i "$dir"
    echo " "

    # The four artwork sources, in the same order run.sh uses.
    python3 ./apple-music-id3tocover.py -i "$dir"
    echo " "
    python3 ./mb-cca-id3tocover.py -i "$dir"
    echo " "
    python3 ./deezer-id3tocover.py -i "$dir"
    echo " "
    python3 ./lastfm-id3tocover.py -i "$dir"
    echo " "

    # Resize/compress whatever cover.jpg now exists in this folder. Neither
    # script has an -i mode; -p works fine here since they simply check
    # every file directly under the given path for one named cover.jpg,
    # without skipping the path itself (unlike the artwork-fetch scripts).
    python3 ./album_cover_reducer_to_1400px.py -p "$dir"
    echo " "
    python3 ./album_cover_compressor_to_jpg90.py -p "$dir"
    echo " "

    # Clean up any cover.jpg/cover.jpg.bak pair left by the resize/compress
    # steps above.
    python3 ./cleanup_cover_art.py -i "$dir"
    echo " "

    # root_cover_remover.py only removes cover.jpg from album-root folders
    # that have CD subfolders — it always skips a path that is itself a CD
    # folder, so this is a harmless no-op here. Included anyway to mirror
    # run.sh's step order exactly.
    python3 ./root_cover_remover.py --confirm -p "$dir"
    echo " "

    # ReplayGain and MP3 validation, scoped to just this one folder.
    bash ./calculate_replaygain.sh -p "$dir"
    echo " "
    bash ./mp3validate.sh -p "$dir"
    echo
done < "$MISSING_FILE"

echo "=========================================="
echo "✅ Retried $total folder(s)."
echo "   Run ./find_missing_covers.sh again to see what's still missing."
echo "=========================================="
