#!/usr/bin/bash
#
# Script: rg-lib.sh
#
# Description:
#   Cache-aware wrapper around calculate_replaygain.sh for full-library
#   ReplayGain processing. Discovers every album directory under a root music
#   path and invokes calculate_replaygain.sh on each one, skipping directories
#   already recorded in a local cache file.
#
#   Use this script when you want to (re-)process the entire library.
#   For new music added by an import or download pipeline, call
#   calculate_replaygain.sh directly with -p pointing at the new album dir.
#
# Usage:
#   rg-lib.sh [-p|--path /path/to/music] [--clear-cache] [--force] [--debug]
#
# Options:
#   -p, --path       Base music directory (overrides artwork-config.ini)
#   --clear-cache    Wipe the cache file before processing
#   --force, -f      Re-process albums even if already cached
#   --debug          Enable bash -x trace output (may appear anywhere in args)
#
# Dependencies:
#   bash, find, grep, calculate_replaygain.sh
#

set -euo pipefail

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

readonly CACHE_FILE="${HOME}/.replaygain_cache.txt"
readonly MAIN_SCRIPT="./calculate_replaygain.sh"
readonly CONFIG_FILE="artwork-config.ini"

# ----------------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------------

# Print usage information and exit.
usage() {
    echo "Usage: $0 [-p|--path /path/to/music] [--clear-cache] [--force] [--debug]"
    exit 0
}

# Check whether a directory path is recorded in the cache.
# Args: $1 - directory path
# Returns: 0 if cached, 1 otherwise
is_cached() {
    local dir="${1%/}"
    grep -Fxq "$dir" "$CACHE_FILE" 2>/dev/null
}

# Append a directory path to the cache file.
# Args: $1 - directory path
add_to_cache() {
    local dir="${1%/}"
    echo "$dir" >> "$CACHE_FILE"
}

# Find all unique parent directories containing MP3 files under a base path.
# Each CD subdirectory is returned as its own entry (multi-disc albums produce
# one cache entry per disc, matching how calculate_replaygain.sh processes them).
# Args: $1 - base directory
# Prints: one directory per line, sorted
find_albums() {
    local base_dir="$1"
    find "$base_dir" -type f -iname "*.mp3" -printf "%h\n" 2>/dev/null | sort -u
}

# Read rootmusicdir from an INI-style config file.
# Args: $1 - config file path
# Prints: the trimmed value, or empty string
read_config_dir() {
    local config="$1"
    grep -v '^#' "$config" \
        | grep -oP '^rootmusicdir\s*=\s*\K.*' \
        | head -1 \
        | sed 's/^[[:space:]]*//;s/[[:space:]]*$//'
}

# ----------------------------------------------------------------------------
# Argument parsing
# ----------------------------------------------------------------------------

debug=false
clear_cache=false
base_dir=""
force=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        -p|--path)
            base_dir="$2"
            shift 2
            ;;
        --clear-cache)
            clear_cache=true
            shift
            ;;
        --force|-f)
            force=true
            shift
            ;;
        --debug)
            debug=true
            shift
            ;;
        --help|-h)
            usage
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

# Activate trace output after all args are parsed so the flag may appear
# anywhere in the argument list.
if [[ "$debug" == true ]]; then
    set -x
fi

# ----------------------------------------------------------------------------
# Initialise cache
# ----------------------------------------------------------------------------

touch "$CACHE_FILE"

if [[ "$clear_cache" == true ]]; then
    : > "$CACHE_FILE"
    echo "✅ Cache cleared"
fi

# ----------------------------------------------------------------------------
# Resolve base directory
# ----------------------------------------------------------------------------

if [[ -z "$base_dir" && -f "$CONFIG_FILE" ]]; then
    base_dir=$(read_config_dir "$CONFIG_FILE")
fi

base_dir="${base_dir%/}"

if [[ -z "$base_dir" || ! -d "$base_dir" ]]; then
    echo "❌ Error: Invalid base directory: ${base_dir:-<not set>}" >&2
    echo "   Specify with -p or configure $CONFIG_FILE" >&2
    exit 1
fi

echo "📁 Base directory: $base_dir"
echo "🗄️  Cache file:     $CACHE_FILE"
echo

# ----------------------------------------------------------------------------
# Validate main script
# ----------------------------------------------------------------------------

if [[ ! -f "$MAIN_SCRIPT" ]]; then
    echo "❌ Error: Main script not found: $MAIN_SCRIPT" >&2
    echo "   Working directory: $(pwd)" >&2
    echo "   Shell scripts present:" >&2
    find . -maxdepth 1 -name '*.sh' 2>/dev/null || echo "   (none)" >&2
    exit 1
fi

if [[ ! -x "$MAIN_SCRIPT" ]]; then
    chmod +x "$MAIN_SCRIPT"
fi

# ----------------------------------------------------------------------------
# Discover albums
# ----------------------------------------------------------------------------

echo "🔍 Finding album directories..."
albums=$(find_albums "$base_dir")

if [[ -z "$albums" ]]; then
    echo "⚠️  No MP3 files found under: $base_dir" >&2
    exit 0
fi

total=$(echo "$albums" | wc -l)
echo "📊 Found $total album director$([ "$total" -eq 1 ] && echo y || echo ies)"
echo

# ----------------------------------------------------------------------------
# Process albums
# ----------------------------------------------------------------------------

processed=0
skipped=0
failed=0

while IFS= read -r album; do
    [[ -z "$album" ]] && continue

    album_name=$(basename "$album")
    mp3_count=$(find "$album" -maxdepth 1 -type f -iname "*.mp3" 2>/dev/null | wc -l)

    if [[ "$force" == false ]] && is_cached "$album"; then
        echo "⏭️  SKIP:       $album_name [$mp3_count MP3s] (cached)"
        skipped=$(( skipped + 1 ))
        continue
    fi

    echo "🎵 PROCESSING: $album_name [$mp3_count MP3s]"
    echo "   Path: $album"

    # Capture the exit code explicitly before any further commands reset $?.
    if bash "$MAIN_SCRIPT" -p "$album"; then
        add_to_cache "$album"
        echo "   ✅ Done"
        processed=$(( processed + 1 ))
    else
        exit_code=$?
        echo "   ❌ Failed (exit $exit_code)"
        failed=$(( failed + 1 ))
    fi
    echo

done <<< "$albums"

# ----------------------------------------------------------------------------
# Summary
# ----------------------------------------------------------------------------

cached_total=$(wc -l < "$CACHE_FILE" 2>/dev/null || echo 0)

echo "========================================="
echo "📊 Summary"
echo "   ✅ Processed:       $processed"
echo "   ⏭️  Skipped (cache): $skipped"
echo "   ❌ Failed:          $failed"
echo "   📁 Total dirs:      $total"
echo "========================================="
echo
echo "Cache: $CACHE_FILE ($cached_total entr$([ "$cached_total" -eq 1 ] && echo y || echo ies))"

if [[ $failed -gt 0 ]]; then
    echo
    echo "⚠️  $failed album(s) failed — review errors above and retry."
    exit 1
fi

echo
echo "✅ All albums processed successfully!"
exit 0
