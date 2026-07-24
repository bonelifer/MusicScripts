## MusicScripts

### Description:
This project consists of a collection of scripts designed to automate various tasks related to managing and organizing music libraries. The scripts handle tasks such as extracting and embedding album cover art, fetching artwork from online sources, processing albums using Picard, and calculating ReplayGain for MP3 files. Each script is designed to be configurable, efficient, and easy to use, making it ideal for managing large music collections.

---

| Filename                  | Description                                                                 |
|---------------------------|-----------------------------------------------------------------------------|
| [Artwork Update Scripts](./artwork-update/README.md) | Fetches, resizes, compresses, and cleans up album cover art from multiple sources, plus ReplayGain and MP3 validation. See that folder's README for the full script list. |
| [Picard Album Processor](./picard_album_processor/DOCS/README-picard_album_processor.md)                   | Automates the processing of music albums using Picard, tracks failures, and restarts Picard if necessary. |

### Instructions:
To run the scripts in the correct order for updating artwork, use the `run.sh` file. For processing albums with Picard, use the `picard_album_processor.sh` script.

---

#### Example Usage:
1. **Update Artwork**:
   ```bash
   ./run.sh
   ```
   This will execute the scripts in the correct sequence to fetch, extract, and embed album artwork.

2. **Process Albums with Picard**:
   ```bash
   ./picard_album_processor.sh
   ```
   This will automate the processing of music albums using Picard.

## **Wiki** Entries:
- [artwork-config.ini](https://github.com/bonelifer/MusicScripts/wiki/artwork%E2%80%90config.ini-Configuration-Options) configuration entry
- [picard-config.ini](https://github.com/bonelifer/MusicScripts/wiki/picard%E2%80%90config.ini-Configuration-Options) configuration entry

## License

This project is licensed under the **GNU General Public License v3.0**.

See [LICENSE](./LICENSE) for more information.
