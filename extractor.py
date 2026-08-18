import json
import re
from datetime import datetime
from typing import Dict, Any, List

def extract_bootstrap_state(html: str) -> dict:
    """Finds the __NEXT_DATA__ script tag and parses the JSON state."""
    match = re.search(r'<script id="__NEXT_DATA__" type="application/json">\s*({.*?})\s*</script>', html)
    if not match:
        # Fallback for when they sometimes omit the id or use a different script
        match = re.search(r'<script[^>]*>\s*(window\.__snapchat_state\s*=\s*({.*?}));?\s*</script>', html)
        if not match:
            raise ValueError("Could not find Snapchat bootstrap JSON in the page source.")
        
        state_match = re.search(r'({.*})', match.group(1))
        if not state_match:
            raise ValueError("Failed to isolate JSON from state script.")
        return json.loads(state_match.group(1))

    return json.loads(match.group(1))

def parse_story(state: dict) -> dict:
    """Extracts metadata and media list from the bootstrap state."""
    props = state.get("props", {})
    page_props = props.get("pageProps", {})
    story = page_props.get("story", {})
    
    # print(json.dumps(story, indent=2)) # debugging structure changes
    
    if not story:
        raise ValueError("Story data is missing from the state payload.")

    snaps = []
    user_info = story.get("userProfile", {})
    username = user_info.get("username", "unknown")
    display_name = user_info.get("displayName", "")

    snap_list = story.get("snapList", [])
    for snap in snap_list:
        snap_id = snap.get("snapId")
        urls = snap.get("snapUrls", {})
        media_url = urls.get("mediaUrl") or urls.get("previewUrl")
        
        if not media_url or not snap_id:
            continue

        raw_ts = snap.get("timestampInSec", 0)
        try:
            timestamp = int(raw_ts)
        except (ValueError, TypeError):
            timestamp = 0

        is_video = snap.get("mediaType", "").lower() == "video" or "mp4" in media_url.lower()

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
