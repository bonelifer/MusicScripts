# picard_album_processor

Batch-runs MusicBrainz Picard against a music library: loads each `ARTIST/ALBUM` folder,
sends it through a fixed Picard command sequence, and sorts the result into a success or
failed-review folder. Tracks progress across runs so re-running only picks up new albums.

See [DOCS/README-picard_album_processor.md](DOCS/README-picard_album_processor.md) for the
full description, options, and logging behavior.

## Quick start

1. Install Picard and confirm it's on `$PATH`:
   ```bash
   picard --version
   ```
2. Copy the example config and fill in your paths:
   ```bash
   cp picard-config.ini.example picard-config.ini
   ```
3. Run it:
   ```bash
   ./picard_album_processor.sh
   ```

## Files

| File | Purpose |
|---|---|
| `picard_album_processor.sh` | The script itself |
| `commands.txt` | Picard command sequence run against each album |
| `picard-config.ini.example` | Template — copy to `picard-config.ini` and fill in |
| `picard-config.ini` | Your actual config (git-ignored) |

See the
[picard-config.ini wiki page](https://github.com/bonelifer/MusicScripts/wiki/picard%E2%80%90config.ini-Configuration-Options)
for its keys.

## License

This project is licensed under the **GNU General Public License v3.0**.

See [LICENSE](../LICENSE) for more information.
