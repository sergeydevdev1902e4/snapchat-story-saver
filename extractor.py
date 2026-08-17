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

