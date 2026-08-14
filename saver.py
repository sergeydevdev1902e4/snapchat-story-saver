import argparse
import json
import sys
from pathlib import Path
import httpx

from snapchat_story_saver.extractor import fetch_story

# TODO: handle custom output naming templates
def get_archive_dir(base_dir: Path, username: str) -> Path:
    path = base_dir / username
    path.mkdir(parents=True, exist_ok=True)
    return path

def load_history(archive_dir: Path) -> set:
    history_file = archive_dir / ".saved_snaps.json"
    if not history_file.exists():
        return set()
    try:
        with open(history_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data)
    except (json.JSONDecodeError, OSError):
        # if corrupted, we just overwrite and redownload
        return set()

def save_history(archive_dir: Path, saved_ids: set):
    history_file = archive_dir / ".saved_snaps.json"
    try:
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(list(saved_ids), f, indent=2)
    except OSError as e:
        print(f"Warning: Could not save history file: {e}", file=sys.stderr)

