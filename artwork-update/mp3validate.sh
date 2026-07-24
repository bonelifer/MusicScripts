#!/usr/bin/bash
#
# mp3validate.sh - Validate and optionally fix MP3 files using `mp3val`.
#
# Uses `artwork-config.ini` to determine the music directory.
# Scans recursively for `.mp3` files and checks each using `mp3val`.
# Logs files with warnings or repairs to /tmp/mp3-errors.txt.
#
# Requires: mp3val
# Usage: ./mp3validate.sh

set -e

# Check for mp3val
if ! command -v mp3val >/dev/null 2>&1; then
    echo "The 'mp3val' utility is required but not installed."
    read -rp "Install mp3val now? [Y/n] " reply
    reply="${reply,,}"  # to lowercase
    if [[ "$reply" =~ ^(y|yes|)$ ]]; then
        sudo apt update && sudo apt install -y mp3val
    else
        echo "Aborting. Please install 'mp3val' manually."
        exit 1
    fi
fi

# Extract rootmusicdir from config
base_dir=$(grep -v '^#' artwork-config.ini | grep -oP '^rootmusicdir\s*=\s*\K.*' | sed 's/^[ \t]*//;s/[ \t]*$//')

if [[ -z "$base_dir" || ! -d "$base_dir" ]]; then
    echo "Error: rootmusicdir not found or not a valid directory in artwork-config.ini"
    exit 1
fi

chk_results="/tmp/mp3-errors.txt"
n=0

[[ -f "$chk_results" ]] && rm -f "$chk_results"
touch "$chk_results"

file_count=$(find "$base_dir" -type f -iname '*.mp3' | wc -l)

if [[ "$file_count" -gt 0 ]]; then
    find "$base_dir" -type f -iname '*.mp3' | while read -r file; do
        n=$((n + 1))
        echo "($n/$file_count) checking $file"

        # Run mp3val and capture output
        output=$(mp3val -f -nb "$file" 2>&1)

        # Log only files with WARNING or FIXED
        if echo "$output" | grep -qE 'WARNING|FIXED'; then
            echo "$file" >> "$chk_results"
            echo "$output" >> "$chk_results"
            echo >> "$chk_results"
        fi
    done
else
    echo "No MP3 files found in $base_dir."
    exit 0
fi

# Output results
if [[ -s "$chk_results" ]]; then
    echo -e "\nThere may be problem(s) with your MP3 files. See below:"
    cat "$chk_results"
else
    echo -e "\n$n files checked, and no problems found."
fi

