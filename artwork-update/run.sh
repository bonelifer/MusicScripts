#!/bin/bash
# Run the album art scripts and replaygain script to process our music files.

python3 ./id3tocovr.py -a
python3 ./id3tocovr.py -a -c
python3 ./embed-artwork.py -c -a
python3 ./embed-artwork.py -a
python3 ./export-coverart.py -c -a
python3 ./export-coverart.py -a
bash ./calculate_replaygain.sh
