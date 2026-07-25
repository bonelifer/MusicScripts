#!/bin/bash
# Run the album art scripts and replaygain script to process our music files.

python3 ./export-coverart.py -c -a
python3 ./export-coverart.py -a

echo " "
python3 ./apple-music-id3tocover.py
echo " "
python3 ./mb-cca-id3tocover.py -a
echo " "
python3 ./deezer-id3tocover.py
echo " "
python3 ./lastfm-id3tocover.py
echo " "

python3 ./album_cover_reducer_to_1400px.py
echo " "
python3 ./album_cover_compressor_to_jpg90.py
echo " "
python3 ./cleanup_cover_art.py -a
echo " "
python3 ./root_cover_remover.py --confirm
echo " "

#curl -X POST http://192.168.1.80:6595/api/removeFinishedDownloads
bash ./calculate_replaygain.sh
echo " "
bash ./mp3validate.sh
