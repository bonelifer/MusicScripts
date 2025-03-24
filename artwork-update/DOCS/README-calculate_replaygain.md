# Calculate ReplayGain for MP3 Files

## Description
This script calculates ReplayGain for MP3 files organized in an ARTIST/ALBUM/CD directory structure. It traverses through the directories, applying album gain and recursive track gain for each album.

## Features
- Calculates album gain for all MP3 files in a directory.
- Applies recursive track gain for each album.
- Supports ARTIST/ALBUM/CD directory structures.
- Easy to configure and use.

## Requirements
- **Bash**: The script is written in Bash and requires a compatible shell.
- **mp3gain**: The `mp3gain` utility must be installed to calculate ReplayGain.
  - Install `mp3gain` on Ubuntu/Debian:
    ```bash
    sudo apt install mp3gain
    ```
  - Install `mp3gain` on macOS (via Homebrew):
    ```bash
    brew install mp3gain
    ```

## Usage
1. **Set the Base Directory**:
   - Open the script in a text editor.
   - Set the `base_dir` variable to the path where your ARTIST folders are located:
     ```bash
     base_dir="/path/to/your/music/library/"
     ```
2. **Run the Script**:
   ```bash
   ./calculate_replaygain.sh
   ```

## Notes
- The script processes MP3 files in the following directory structure:
  ```
  ARTIST/
    ALBUM/
      CD/
        *.mp3
  ```
- It skips non-MP3 files and directories that do not match the expected structure.
- ReplayGain tags are written directly to the MP3 files.

## License

This project is licensed under the **GNU General Public License v3.0**.

See [LICENSE](../../LICENSE) for more information.