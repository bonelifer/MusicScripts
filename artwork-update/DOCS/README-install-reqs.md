# Install Dependencies

## Description
`install-reqs.sh` installs every dependency the scripts in this directory need, as documented
across each script's own `DOCS/README-*.md`. It's the union of every "Installation" section in
this folder: five Python packages via `pip`, and two system packages via `apt`. Not every script
needs every package — see the individual doc in `DOCS/` for exactly which packages a given
script requires.

## Features
- Installs all five Python packages (`mutagen`, `musicbrainzngs`, `requests`, `Pillow`,
  `itunespy`) in one `pip` call.
- Falls back to `pip install --break-system-packages` automatically if the system blocks pip
  with the `externally-managed-environment` error (PEP 668, the default on Debian 12+/Ubuntu
  23.04+), since this project doesn't use a virtual environment. Prints a warning when it does.
- Checks whether `mp3gain`/`mp3val` are already on `$PATH` before prompting, so re-running after
  a partial install doesn't re-prompt for packages you already have.
- Prompts before using `sudo apt install` for the missing system packages; skips cleanly if you
  decline, printing what you'll need to install manually.

## Requirements
- **Python 3.x** with `pip`
- **apt** (Debian/Ubuntu). On other systems, install `mp3gain` and `mp3val` manually first, then
  run this script to handle the Python packages.

## Usage
```bash
./install-reqs.sh
```
No arguments or flags.

## Notes
- The `--break-system-packages` fallback carries real risk of clashing with apt-managed Python
  packages on your system. A virtual environment is the safer long-term fix, but none of the
  scripts in this directory currently activate one, so this script matches that existing
  convention rather than introducing a venv on its own.
- Declining the `apt` prompt doesn't stop the script — it just leaves `mp3gain`/`mp3val`
  uninstalled, which will only matter if you run `calculate_replaygain.sh`/`replaygain-library.sh`
  (`mp3gain`) or `mp3validate.sh` (`mp3val`, which also offers its own install prompt the first
  time it's run).

## License

This project is licensed under the **GNU General Public License v3.0**.

See [LICENSE](../../LICENSE) for more information.
