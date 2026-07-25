#!/usr/bin/bash
#
# find_missing_covers.sh
#
# Description:
#   Scans a music library for multi-disc "CD N" subfolders and reports every
#   one that has no cover.jpg directly inside it. Useful for spotting CD
#   subfolders the cover-art scripts in this directory haven't produced a
#   cover for yet.
#
# Requirements:
#   - bash, find
#   - artwork-config.ini with [paths] rootmusicdir (unless --path is given)
#
# Usage:
#   ./find_missing_covers.sh [-p|--path /path/to/music]
#
# Options:
#   -p, --path   Directory to scan. Overrides rootmusicdir from
#                artwork-config.ini for this run.
#
# Output:
#   Writes one folder path per line to missing_covers.txt (git-ignored,
#   since it's a per-run report rather than project source) in the current
#   directory. Any existing missing_covers.txt is overwritten.
#

set -e

readonly CONFIG_FILE="artwork-config.ini"

# Where results are written; one "CD *" folder path per line.
OUTPUT_FILE="missing_covers.txt"

# ----------------------------------------------------------------------------
# Argument parsing
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
# Resolve music directory: -p wins, otherwise read rootmusicdir from config
# ----------------------------------------------------------------------------

if [[ -n "$path_override" ]]; then
    music_dir="$path_override"
else
    if [[ ! -f "$CONFIG_FILE" ]]; then
        echo "Error: No --path given and $CONFIG_FILE not found." >&2
        exit 1
    fi
    music_dir=$(grep -v '^#' "$CONFIG_FILE" \
        | grep -oP '^rootmusicdir\s*=\s*\K.*' \
        | head -1 \
        | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

    if [[ -z "$music_dir" ]]; then
        echo "Error: Could not read rootmusicdir from $CONFIG_FILE" >&2
        exit 1
    fi
fi

music_dir="${music_dir%/}"

if [[ ! -d "$music_dir" ]]; then
    echo "Error: music directory not found: $music_dir" >&2
    exit 1
fi

# ----------------------------------------------------------------------------
# Scan: only "CD *" subfolders are checked; top-level album folders without
# a CD subfolder are ignored.
# ----------------------------------------------------------------------------

# Find every directory named "CD <something>" anywhere under music_dir.
find "$music_dir" -type d -name "CD *" | while read -r dir; do
    # Check for a cover.jpg (case-insensitive) directly inside this CD
    # folder, without descending into any deeper subfolders. -maxdepth 1
    # keeps the check scoped to this folder only; -print -quit stops at
    # the first match instead of scanning the whole folder for a yes/no
    # question.
    if [ -z "$(find "$dir" -maxdepth 1 -iname "cover.jpg" -print -quit)" ]; then
        # No cover.jpg found in this CD folder: record its path.
        echo "$dir"
    fi
done > "$OUTPUT_FILE"
