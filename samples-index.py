#!/usr/bin/python3
# Copyright 2026 Google LLC
import os
import re
import json
import pathlib
import itertools
from typing import Dict, List, Optional, Any, Tuple
from urllib.request import urlopen

# --- Configuration: Ultimate Time/Space Standards ---
BASE_URI = "https://github.com/google/google-api-python-client/tree/main/"
DISCOVERY_URL = "https://www.googleapis.com/discovery/v1/apis"

def get_api_directory() -> Dict[str, Any]:
    """TIME: O(M) fetch and parse. SPACE: O(M) memory footprint."""
    try:
        with urlopen(DISCOVERY_URL, timeout=10) as response:
            data = json.loads(response.read().decode())
            return {item["name"]: item for item in data.get("items", []) if item.get("preferred")}
    except Exception as e:
        print(f"Offline Mode: Discovery unreachable. Error: {e}")
        return {}

# Static lookup for keywords
KEYWORDS = {
    "appengine": "Google App Engine",
    "oauth2": "OAuth 2.0",
    "cmdline": "Command-line",
    "django": "Django",
    "media": "Media Upload/Download",
}

DIRECTORY = get_api_directory()

def wiki_escape(s: str) -> str:
    """Regex optimized for CamelCase escaping."""
    return re.sub(r"([A-Z]+[a-z]+[A-Z])", r"!\1", s)

def get_metadata(lines: List[str]) -> Dict[str, List[str]]:
    """O(L) Time: Single-pass scan of README lines."""
    meta = {"api": [], "keywords": [], "uri": []}
    for line in lines:
        for key in meta:
            if line.startswith(f"{key}:"):
                meta[key].extend(line[len(key)+1:].strip().split())
    return meta

def scan_samples(base_path: str) -> Tuple[List[tuple], set]:
    """ULTIMATE SPACE: Pathlib rglob avoids recursive stack overflow."""
    samples = []
    found_keywords = set()
    path = pathlib.Path(base_path)
    
    if not path.exists():
        return [], set()

    for readme in path.rglob("README"):
        try:
            with open(readme, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
                desc = " ".join(itertools.takewhile(lambda x: x.strip(), lines))
                meta = get_metadata(lines)
                
                api = meta["api"][0] if meta["api"] else None
                uri = meta["uri"][0] if meta["uri"] else (BASE_URI + str(readme.parent))
                
                found_keywords.update(meta["keywords"])
                samples.append((api, meta["keywords"], str(readme.parent), desc, uri))
        except Exception:
            continue

    samples.sort(key=lambda x: (x[0] or "", x[2]))
    return samples, found_keywords

def main():
    samples, keyword_set = scan_samples("./samples")
    page = ['<wiki:toc max_depth="3" />\n= Samples By API =\n']
    
    current_api = None
    for api, kws, dirname, desc, uri in samples:
        if not api or api not in DIRECTORY:
            continue
            
        entry = DIRECTORY[api]
        if current_api != api:
            current_api = api
            header = (
                f"\n=== {entry['icons']['x32']} {wiki_escape(entry.get('title', api))} ===\n\n"
                f"{wiki_escape(entry.get('description', ''))}\n\n"
                f"[Documentation](https://developers.google.com/api-client-library/python/apis/{api}/{entry['version']})\n\n"
            )
            page.append(header)
            
        page.append(f"|| [{uri} {dirname}] || {wiki_escape(desc)} ||\n")

    # Output generation
    print("".join(page))

if __name__ == "__main__":
    main()