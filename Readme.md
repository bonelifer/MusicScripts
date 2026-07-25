# MusicScripts

Two independent script collections for maintaining a local music library: fetching and
resizing album cover art, and automating MusicBrainz Picard imports.

| Project | Purpose |
|---|---|
| [artwork-update](./artwork-update/README.md) | Fetches album covers from four sources, resizes/compresses them, cleans up backups and redundant copies, applies ReplayGain, and validates MP3s. |
| [picard_album_processor](./picard_album_processor/README.md) | Batch-runs MusicBrainz Picard against a library, tracking successes/failures and restarting Picard as needed. |

## Usage

Each project's own README has the full script list, setup steps, and command reference. The
short version:

```bash
cd artwork-update
./install-reqs.sh   # one-time: install dependencies
./run.sh             # fetch/resize/compress covers, ReplayGain, MP3 validation
```

```bash
cd picard_album_processor
./picard_album_processor.sh
```

## Wiki entries
- [artwork-config.ini](https://github.com/bonelifer/MusicScripts/wiki/artwork%E2%80%90config.ini-Configuration-Options) configuration reference
- [picard-config.ini](https://github.com/bonelifer/MusicScripts/wiki/picard%E2%80%90config.ini-Configuration-Options) configuration reference

## License

This project is licensed under the **GNU General Public License v3.0**.

See [LICENSE](./LICENSE) for more information.
