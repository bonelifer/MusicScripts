#!/bin/bash

# Script: Picard Album Processor
# Description: This script automates the processing of music albums using Picard.
# It moves successfully processed albums to a designated output directory, tracks failures,
# and restarts Picard if necessary.
# 
# Features:
# - Process albums using Picard with custom commands.
# - Track processed and failed albums in separate log files.
# - Automatically restart Picard if it's not running.
# - Remove empty artist directories after processing.
# 
# Usage:
# Ensure Picard and the commands file (commands.txt) are available.
# Run the script using:
# $ ./picard.sh

# Directory paths for music, output, and failed albums
music_directory="/home/username/MusicToOrganize/"
output_directory="/home/username/MusicToOrganize/Picard/"
failed_directory="$music_directory/Failed"

# Ensure the output and failed directories exist
mkdir -p "$output_directory"
mkdir -p "$failed_directory"

# Files to track failed and processed albums
failed_albums_file="$music_directory/failed_albums.txt"
processed_albums_file="$music_directory/processed_albums.txt"
touch "$failed_albums_file" "$processed_albums_file"

# Function to process albums using Picard
process_album() {
    local album_dir="$1"
    local artist_dir="$2"

    echo "Processing album: $album_dir"

    # Execute Picard with the provided commands and handle success or failure
    if picard -e LOAD "$album_dir" -e FROM_FILE ./commands.txt; then
        echo "Successfully processed: $album_dir"
        
        # Ensure the artist directory exists in the output directory
        mkdir -p "$output_directory/$(basename "$artist_dir")"
        
        # Move processed album to the output directory
        mv "$album_dir" "$output_directory/$(basename "$artist_dir")/"
        
        # Log successful processing
        echo "$album_dir" >> "$processed_albums_file"
    else
        echo "Picard encountered an error with: $album_dir"
        
        # Log the failed album
        echo "$album_dir" >> "$failed_albums_file"
        
        # Ensure the artist directory exists in the failed directory
        mkdir -p "$failed_directory/$(basename "$artist_dir")"
        
        # Move failed album to the failed directory for review
        mv "$album_dir" "$failed_directory/$(basename "$artist_dir")/"
    fi
}

# Function to check if Picard is currently running
is_picard_running() {
    if pgrep -x "picard" > /dev/null; then
        return 0  # Picard is running
    else
        return 1  # Picard is not running
    fi
}

# Function to restart Picard if it's not running
restart_picard_if_needed() {
    if ! is_picard_running; then
        echo "Picard is not running. Restarting Picard..."
        picard &
        sleep 5  # Allow Picard some time to start
    fi
}

# Function to check if a directory is empty
is_directory_empty() {
    local dir="$1"
    if [ -z "$(ls -A "$dir")" ]; then
        return 0  # Directory is empty
    else
        return 1  # Directory is not empty
    fi
}

# Function to remove empty artist directories
remove_empty_artist_directories() {
    local artist_dir="$1"
    if is_directory_empty "$artist_dir"; then
        echo "Removing empty artist directory: $artist_dir"
        rmdir "$artist_dir"
    fi
}

# Main processing loop
while true; do
    # Ensure Picard is running
    restart_picard_if_needed

    # Track whether albums were processed in this round
    albums_processed=0

    # Iterate over each artist directory in the music directory
    for artist_dir in "$music_directory"/*/; do
        # Normalize paths to handle symbolic links and absolute paths
        normalized_artist_dir=$(realpath "$artist_dir")
        normalized_failed_dir=$(realpath "$failed_directory")

        # Skip the failed directory to avoid redundant processing
        if [[ "$normalized_artist_dir" == "$normalized_failed_dir" ]]; then
            echo "Skipping Failed directory: $artist_dir"
            continue
        fi

        # Ensure the path is a directory
        if [ -d "$artist_dir" ]; then
            echo "Processing artist: $artist_dir"

            # Iterate through each album directory within the artist directory
            for album_dir in "$artist_dir"/*/; do
                if [ -d "$album_dir" ]; then
                    # Skip previously failed albums
                    if grep -Fxq "$album_dir" "$failed_albums_file"; then
                        echo "Skipping previously failed album: $album_dir"
                        continue
                    fi

                    # Skip previously processed albums
                    if grep -Fxq "$album_dir" "$processed_albums_file"; then
                        echo "Skipping previously processed album: $album_dir"
                        continue
                    fi

                    # Skip empty album directories
                    if is_directory_empty "$album_dir"; then
                        echo "Skipping empty album directory: $album_dir"
                        continue
                    fi

                    # Process the album using Picard
                    process_album "$album_dir" "$artist_dir"
                    albums_processed=1
                fi
            done

            # Remove the artist directory if all albums are processed and it is empty
            remove_empty_artist_directories "$artist_dir"
        fi
    done

    # Exit if no albums were processed in this round
    if [ "$albums_processed" -eq 0 ]; then
        echo "No albums processed in this round. Exiting."
        break
    else
        echo "Starting another round of processing..."
    fi
done

echo "Script completed."

