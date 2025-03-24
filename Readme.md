## MusicScripts

### Description:
This project consists of a collection of scripts designed to automate various tasks related to managing and organizing music libraries. The scripts handle tasks such as extracting and embedding album cover art, fetching artwork from online sources, processing albums using Picard, and calculating ReplayGain for MP3 files. Each script is designed to be configurable, efficient, and easy to use, making it ideal for managing large music collections.

---

| Filename                  | Description                                                                 |
|---------------------------|-----------------------------------------------------------------------------|
| [ID3 to Cover Art Fetcher](./artwork-update/DOCS/README-id3tocovr.md)             | Fetches album artwork from multiple sources and embeds it into MP3 files.   |
| [Export Cover Art from MP3 Files](./artwork-update/DOCS/README-export-coverart.md) | Extracts and saves album cover art from MP3 files to `cover.jpg`.           |
| [Embed and Check Artwork Resolution in Music Files](./artwork-update/DOCS/README-embed-artwork.md)     | Embeds and checks the resolution of album cover art in MP3 files.           |
| [Calculate ReplayGain for MP3 Files](./artwork-update/DOCS/README-calculate_replaygain.md) | Calculates ReplayGain for MP3 files organized in an ARTIST/ALBUM/CD directory structure. |
| [Picard Album Processor](./picard_album_processor/DOCS/Readme-picard_album_processor.md)                   | Automates the processing of music albums using Picard, tracks failures, and restarts Picard if necessary. |

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

## **Wiki** Entry: 
[artwork-config.ini](https://github.com/bonelifer/MusicScripts/wiki/artwork%E2%80%90config.ini-Configuration-Options) configuration entry

## License

This project is licensed under the **GNU General Public License v3.0**.

See [LICENSE](./LICENSE) for more information.
