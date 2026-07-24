# MP3 File Validator

## Description
`mp3validate.sh` recursively scans `rootmusicdir` for `.mp3` files and checks each one with
`mp3val`, reporting any file that triggers a warning or gets auto-fixed.

## Features
- Prompts to install `mp3val` via `apt` if it isn't already present.
- Reads `rootmusicdir` from `artwork-config.ini`.
- Runs `mp3val -f -nb` (auto-fix, no backup) against every MP3 found.
- Collects only files with `WARNING` or `FIXED` output into a results file.
- Prints a running `(n/total)` progress line while scanning.

## Requirements
- **Bash**
- **mp3val** (offered for auto-install via `apt` if missing)
- `artwork-config.ini` with `[paths] rootmusicdir`

## Usage
```bash
./mp3validate.sh
```
No arguments or flags.

## Logging
Results (files with warnings, or that `mp3val` fixed) are written to `/tmp/mp3-errors.txt`,
which is overwritten on each run. If no MP3 has issues, a one-line summary is printed instead
and the results file is left empty.

## Notes
- `mp3val -f` auto-fixes issues in place — this rewrites the affected MP3 files. There is no
  dry-run mode.
- The install prompt only supports `apt`; on non-Debian systems, install `mp3val` manually
  first.

## License

This project is licensed under the **GNU General Public License v3.0**.

See [LICENSE](../../LICENSE) for more information.
