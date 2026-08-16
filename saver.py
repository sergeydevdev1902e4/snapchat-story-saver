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

def main():
    parser = argparse.ArgumentParser(
        description="Archive public Snapchat stories before they expire."
    )
    parser.add_argument("username", help="Snapchat username to download stories from")
    parser.add_argument(
        "-o", "--output",
        default=".",
        help="Base output directory (default: current directory)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force download of already saved snaps"
    )

    args = parser.parse_args()

    base_dir = Path(args.output)
    archive_dir = get_archive_dir(base_dir, args.username)
    history = load_history(archive_dir)

    print(f"Fetching story for '{args.username}'...")
    try:
        snaps = fetch_story(args.username)
    except Exception as e:
        print(f"Error fetching story: {e}", file=sys.stderr)
        sys.exit(1)

    if not snaps:
        print("No active public stories found.")
        return

    print(f"Found {len(snaps)} active snaps. Checking for new media...")

    new_snaps_count = 0
    with httpx.Client(timeout=10.0) as client:
        for snap in snaps:
            snap_id = snap.get("id")
            url = snap.get("url")
            media_type = snap.get("type", "mp4")

            if not snap_id or not url:
                continue

            if snap_id in history and not args.force:
                # print(f"DEBUG: {snap_id} already saved, skipping")
                continue

            ext = "jpg" if media_type == "image" else "mp4"
            filename = f"{args.username}_{snap_id}.{ext}"
            dest = archive_dir / filename

            print(f"Downloading {filename}...")
            if downloadSnap(client, url, dest):
                history.add(snap_id)
                new_snaps_count += 1

    if new_snaps_count > 0:
        save_history(archive_dir, history)
        print(f"Successfully archived {new_snaps_count} new snaps.")
    else:
        print("No new snaps to download.")

if __name__ == "__main__":
    main()
