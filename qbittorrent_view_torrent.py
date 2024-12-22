import argparse
import logging
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Any, NewType, Union
import bencodepy  # type: ignore


### ---------- SETUP ---------- ###

# python 3.6+
# pip install bencodepy

### ---------- SETUP ---------- ###

### ---------- CONFIG ----------

# This must be the path from the prespective of this script
# It may differ from the path you have in cross-seed
TORRENT_DIR = "." #"/containers/qbittorrent/config/data/BT_backup"

### ---------- END CONFIG ----------


# types
FastResume = NewType("FastResume", OrderedDict[bytes, Any])
Torrent = NewType("Torrent", OrderedDict[bytes, Any])
PathScript = NewType("PathScript", Path)
PathQbit = NewType("PathQbit", Path)

assert sys.version_info >= (3, 6), f'Python 3.6+ required, current version: {sys.version_info}'
assert isinstance(TORRENT_DIR, str), 'TORRENT_DIR must be a string like: TORRENT_DIR = "/path/to/folder"'
TORRENT_DIR_PATH = PathScript(Path(TORRENT_DIR))
assert TORRENT_DIR_PATH.exists() and TORRENT_DIR_PATH.is_dir(), f'TORRENT_DIR does not exist or is not a folder: {TORRENT_DIR}'

# Logging
LOG_NAME = f"{Path(__file__).stem}.log"
LOG_FORMAT_DATE = "%Y-%m-%d %H:%M:%S"; LOG_FORMAT_STREAM = "%(asctime)s.%(msecs)03d %(levelname)s: %(message)s"; LOG_FORMAT_FILE = "%(asctime)s.%(msecs)03d %(levelname)s: %(message)s"
LOG_HANDLER_STREAM = logging.StreamHandler(sys.stdout)
LOG_HANDLER_FILE = logging.FileHandler(LOG_NAME)
LOG_HANDLER_STREAM.setFormatter(logging.Formatter(LOG_FORMAT_STREAM, LOG_FORMAT_DATE)); LOG_HANDLER_FILE.setFormatter(logging.Formatter(LOG_FORMAT_FILE, LOG_FORMAT_DATE))
log = logging.getLogger(LOG_NAME)
log.setLevel(logging.DEBUG); LOG_HANDLER_STREAM.setLevel(logging.DEBUG); LOG_HANDLER_STREAM.setLevel(logging.DEBUG)
log.addHandler(LOG_HANDLER_STREAM)
log.addHandler(LOG_HANDLER_FILE)

# Argument parsing
parser = argparse.ArgumentParser(description="Filter torrents by name or hash.")
parser.add_argument(
    "-search",
    type=str,
    help="Filter torrents by a substring in the torrent name or hash.",
    default=""
)
args = parser.parse_args()
search_term = args.search.lower()

for fastresume_file in TORRENT_DIR_PATH.glob("*.fastresume"):
    fastresume: FastResume = bencodepy.decode_from_file(fastresume_file)  # type: ignore

    torrent_hash: str = fastresume_file.stem
    torrent_file = TORRENT_DIR_PATH/f"{torrent_hash}.torrent"
    if not torrent_file.exists():
        log.error(f"Torrent file not found: {torrent_file}")
        continue

    torrent: Torrent = bencodepy.decode_from_file(torrent_file)  # type: ignore
    info_dict: dict[bytes, Any] = torrent[b'info']  # type: ignore
    info_name: bytes = info_dict[b'name']  # type: ignore
    torrent_name: str = info_name.decode()

    if search_term and search_term not in torrent_name.lower() and search_term not in torrent_hash.lower():
        continue

    log.info(f"{torrent_name} [{torrent_hash}]")