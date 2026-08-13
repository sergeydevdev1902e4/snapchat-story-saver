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

