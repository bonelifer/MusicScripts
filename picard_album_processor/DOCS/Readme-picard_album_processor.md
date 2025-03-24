# Picard Album Processor

## Overview
The **Picard Album Processor** is a Bash script designed to automate the processing of music albums using MusicBrainz Picard. It organizes successfully processed albums, tracks failures, and manages empty directories. Additionally, it ensures Picard is running during the operation and restarts it if necessary.

## Features
- **Automated Processing**: Runs Picard with a specified commands file.
- **Error Tracking**: Logs failed albums for later review.
- **Success Tracking**: Keeps a record of processed albums to avoid duplication.
- **Directory Management**: Moves successful albums to the output directory and failed albums to a designated folder.
- **Picard Management**: Ensures Picard is running and restarts if necessary.
- **Empty Directory Cleanup**: Removes artist directories if they are empty.

## Prerequisites
- Linux or macOS
- Bash 4.0+
- MusicBrainz Picard installed and available in `$PATH`
- `commands.txt` file with Picard commands

## Installation
1. Copy the script to a folder in your `$PATH`.

2. Ensure the script has executable permissions.
    ```bash
    chmod +x picard_album_processor.sh
    ```

3. Verify Picard is installed and accessible.
    ```bash
    picard --version
    ```

4. **Update Folder Paths**:
   Open the script in a text editor and update the following variables to match your directory structure:
   ```bash
   music_directory="/home/username/MusicToOrganize/"  # Replace with your music source directory
   output_directory="/home/username/MusicToOrganize/Picard/""  # Replace with your output directory
   failed_directory="$music_directory/Failed"  # Leave as is
   ```

## Usage
Run the script using the following command:
```bash
./picard_album_processor.sh
```
The script will process the albums located in the `music_directory` directory, moving successfully processed albums to `output_directory` and failed albums to `failed_directory`.

### File Structure Example
```bash
/path/to/Music/for/processing/
├── Artist1/
│   ├── Album1/
│   └── Album2/
└── Artist2/
    └── Album1/
```

### Commands File
Ensure you have a `commands.txt` file containing the required Picard commands for processing.

## Logs
- **`failed_albums.txt`**: Tracks albums that failed processing.
- **`processed_albums.txt`**: Tracks albums that were successfully processed.

## Troubleshooting
- **Picard Fails to Start**: Verify Picard is installed and available in the system’s path.
- **Albums Not Processed**: Ensure the commands in `commands.txt` are correct.
- **Permissions Issues**: Check directory and file permissions with `ls -l`.

## License

This project is licensed under the **GNU General Public License v3.0**.

See [LICENSE](../../LICENSE) for more information.
