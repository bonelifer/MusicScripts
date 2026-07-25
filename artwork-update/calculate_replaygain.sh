#!/usr/bin/bash
#
# Script: calculate_replaygain.sh
#
# Description:
#   Calculates ReplayGain for MP3 files using mp3gain. Designed for two
#   distinct calling contexts:
#
#   1. New-music workflow (called by another script, e.g. a download/import
#      pipeline): receives a single leaf directory (one album or CD) via -p
#      and processes it immediately.
#
#   2. Standalone / full-library use: receives a root music directory and
#      traverses the full ARTIST/ALBUM/[CD] tree. For bulk re-processing of
#      the entire library, prefer replaygain-library.sh, which adds cache-based skipping.
#
#   In both cases the entry point auto-detects whether the given path is a
#   leaf (contains MP3s directly) or a root (requires traversal).
#
# Requirements:
#   - mp3gain
#   - artwork-config.ini with rootmusicdir (unless --path is specified)
#
# Usage:
#   ./calculate_replaygain.sh [-p|--path /path/to/music]
#
# Options:
#   -p, --path   Directory to process (leaf album/CD dir, or root music dir)
#

set -euo pipefail

readonly CONFIG_FILE="artwork-config.ini"

# ----------------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------------

# Return true if a directory contains MP3 files at its top level.
# Uses -quit to stop at the first match, avoiding a grep pipe.
# Args: $1 - directory to check
has_mp3s() {
    local directory="$1"
    local result
    result=$(find "$directory" -maxdepth 1 -type f -iname "*.mp3" -print -quit)
    [[ -n "$result" ]]
}

# Apply album-level and track-level ReplayGain to all MP3s in a directory.
# Collects the file list once and reuses it for both mp3gain passes.
# Args: $1 - directory containing MP3 files (non-recursive)
calculate_album_gain() {
    local directory="$1"
    echo "  🎚️  Applying gain: $directory"

    # Collect MP3 paths once to avoid running find twice.
    local mp3_files=()
    while IFS= read -r -d '' f; do
        mp3_files+=("$f")
    done < <(find "$directory" -maxdepth 1 -type f -iname "*.mp3" -print0)

    [[ ${#mp3_files[@]} -eq 0 ]] && return 0

    # Album gain pass: tags all files with a shared album gain value.
    # -a  album gain mode  -s i  skip already-tagged  -k  avoid clipping
    mp3gain -a -s i -k "${mp3_files[@]}"

    # Track gain pass: applies per-track gain on top of album gain.
    mp3gain -r -s i -k "${mp3_files[@]}"
}

# Traverse a root music directory with ARTIST/ALBUM/[CD] structure and apply
# ReplayGain to each album or CD subdirectory found.
# Args: $1 - root music directory
traverse_directories() {
    local base_directory="$1"

    while IFS= read -r -d '' artist_dir; do
        echo "🎤 Artist: $(basename "$artist_dir")"

        while IFS= read -r -d '' album_dir; do
            echo "  💿 Album: $(basename "$album_dir")"

            # Collect CD subdirectories (multi-disc releases).
            local cd_dirs=()
            while IFS= read -r -d '' cd_dir; do
                cd_dirs+=("$cd_dir")
            done < <(find "$album_dir" -mindepth 1 -maxdepth 1 -type d -print0 | sort -z)

            if [[ ${#cd_dirs[@]} -gt 0 ]]; then
                # Process each disc subdirectory independently.
                for cd_dir in "${cd_dirs[@]}"; do
                    calculate_album_gain "$cd_dir"
                done
            elif has_mp3s "$album_dir"; then
                # No CD subdirs: process MP3s directly in the album directory.
                calculate_album_gain "$album_dir"
            fi

        done < <(find "$artist_dir" -mindepth 1 -maxdepth 1 -type d -print0 | sort -z)

    done < <(find "$base_directory" -mindepth 1 -maxdepth 1 -type d -print0 | sort -z)
}

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
# Resolve base directory
# ----------------------------------------------------------------------------

if [[ -n "$path_override" ]]; then
    base_dir="$path_override"
else
    if [[ ! -f "$CONFIG_FILE" ]]; then
        echo "❌ Error: No --path given and $CONFIG_FILE not found." >&2
        exit 1
    fi
    base_dir=$(grep -v '^#' "$CONFIG_FILE" \
        | grep -oP '^rootmusicdir\s*=\s*\K.*' \
        | head -1 \
        | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

    if [[ -z "$base_dir" ]]; then
        echo "❌ Error: Could not read rootmusicdir from $CONFIG_FILE" >&2
        exit 1
    fi
fi

base_dir="${base_dir%/}"

if [[ ! -d "$base_dir" ]]; then
    echo "❌ Error: Directory does not exist: $base_dir" >&2
    exit 1
fi

echo
echo "📁 Base directory: $base_dir"
echo "Starting ReplayGain calculation..."

# ----------------------------------------------------------------------------
# Entry point: leaf directory or full tree
# ----------------------------------------------------------------------------

# Leaf directory (MP3s present at top level): process as a single album/CD.
# Typical case: called by an import/download pipeline for newly added music.
#
# Root directory (no MP3s at top level): traverse the full ARTIST/ALBUM/[CD]
# tree. For cache-aware full-library runs, use replaygain-library.sh instead.
if has_mp3s "$base_dir"; then
    calculate_album_gain "$base_dir"
else
    traverse_directories "$base_dir"
fi

echo "✅ ReplayGain calculation complete!"
