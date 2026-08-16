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

def downloadSnap(client: httpx.Client, url: str, dest_path: Path) -> bool:
    """Download a single media file to the destination path."""
    try:
        response = client.get(url, follow_redirects=True)
        if response.status_code != 200:
            print(f"Failed to download {url}: HTTP {response.status_code}", file=sys.stderr)
            return False
        dest_path.write_bytes(response.content)
        return True
    except httpx.HTTPError as e:
        print(f"Network error downloading {url}: {e}", file=sys.stderr)
        return False

