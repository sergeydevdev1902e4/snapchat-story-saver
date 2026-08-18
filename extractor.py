import json
import re
from datetime import datetime
from typing import Dict, Any, List

def extract_bootstrap_state(html: str) -> dict:
    """Finds the __NEXT_DATA__ script tag or state block and parses it."""
    match = re.search(r'<script id="__NEXT_DATA__" type="application/json">\s*(.*?)\s*</script>', html, re.DOTALL)
    if not match:
        # Snapchat changed hydration state tags in recent web updates
        match = re.search(r'<script id="main-sc-state" type="application/json">\s*(.*?)\s*</script>', html, re.DOTALL)
        if not match:
            raise ValueError("Could not find Snapchat bootstrap or hydration JSON state.")
        
    return json.loads(match.group(1))

def parse_story(state: dict) -> dict:
    """Extracts metadata and media list from the bootstrap state.
    
    Handles multiple nested shapes since Snapchat shifts these keys regularly.
    """
    props = state.get("props", {})
    page_props = props.get("pageProps", {})
    
    # Sometimes it is under pageProps.story, other times nested inside storyResponse
    story = page_props.get("story")
    if not story:
        story_resp = page_props.get("storyResponse", {})
        story = story_resp.get("story") if isinstance(story_resp, dict) else None

    if not story:
        # Fallback for spotlight or curated context profiles
        story = page_props.get("curatedStories", [{}])[0] if page_props.get("curatedStories") else {}

    # print(json.dumps(story, indent=2)) # debugging structure changes

    # Profile info moves around too
    user_info = story.get("userProfile") or page_props.get("userProfile") or {}
    username = user_info.get("username") or page_props.get("username") or "unknown"
    display_name = user_info.get("displayName") or user_info.get("field_display_name") or ""

    username = username.strip().lower()

    snaps = []
    snap_list = story.get("snapList") or story.get("snaps") or []
    for snap in snap_list:
        snap_id = snap.get("snapId") or snap.get("id")
        urls = snap.get("snapUrls") or snap.get("urls") or {}
        media_url = urls.get("mediaUrl") or urls.get("previewUrl") or snap.get("url")
        
        if not media_url or not snap_id:
            continue

        # Fix relative paths to fully qualified URIs
        if media_url.startswith("//"):
            media_url = "https:" + media_url

        raw_ts = snap.get("timestampInSec") or snap.get("timestamp") or 0
        try:
            timestamp = int(float(raw_ts))
        except (ValueError, TypeError):
            timestamp = 0

        media_type = str(snap.get("mediaType", "")).upper()
        is_video = "VIDEO" in media_type or "mp4" in media_url.lower()

        snaps.append({
            "id": snap_id,
            "url": media_url,
            "timestamp": timestamp,
            "is_video": is_video,
            "captured_at": datetime.fromtimestamp(timestamp).isoformat() if timestamp else None
        })

    return {
        "username": username,
        "display_name": display_name,
        "snaps": snaps
    }
