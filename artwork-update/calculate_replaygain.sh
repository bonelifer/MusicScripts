#!/bin/bash

# Script: calculate_replaygain.sh
#
# Description:
# This script calculates ReplayGain for MP3 files organized in an ARTIST/ALBUM/CD directory structure.
# It traverses through the directories, applying album gain and recursive track gain for each album.
#
# Usage: 
# 1. Set the base directory where your ARTIST folders are located in the 'base_dir' variable.
# 2. Execute the script using './calculate_replaygain.sh'.
#

# Editable Variable
base_dir="/media/william/NewData/Music/MP3-OLD/"

# Function to calculate album gain for a given directory
calculate_album_gain() {
    local directory="$1"
    echo "Processing directory: $directory"
    
    # Calculate album gain for all mp3 files in the directory
    find "$directory" -type f -name "*.mp3" -exec mp3gain -a -s i -k '{}' +
    
    # Calculate track gain for all mp3 files in the directory (recursive)
    mp3gain -r -s i -k "$directory"/*.mp3
}

# Main function to traverse through ARTIST/ALBUM/CD directory structure
traverse_directories() {
    local base_directory="$1"
    cd "$base_directory" || return

    # Find all ARTIST directories
    for artist_dir in */; do
        if [ -d "$artist_dir" ]; then
            cd "$artist_dir" || continue

            # Find all ALBUM directories for each artist
            for album_dir in */; do
                if [ -d "$album_dir" ]; then
                    cd "$album_dir" || continue

                    # Find all CD directories for each album
                    for cd_dir in */; do
                        if [ -d "$cd_dir" ]; then
                            calculate_album_gain "$cd_dir"
                        fi
                    done

                    cd ..
                fi
            done

            cd ..
        fi
    done
}

# Start traversing from the base directory where your ARTIST folders are located
traverse_directories "$base_dir"

