#!/usr/bin/env python3
# Copyright 2026 Google LLC

import argparse
import shutil
import sys
from pathlib import Path

# --- Configuration: Optimized for 2026 Standards ---
# Ignore internal library folders and VCS metadata
IGNORE = {".hg", ".git", "httplib2", "oauth2", "simplejson", "static"}
IGNORE_IN_SAMPLES = {"googleapiclient", "oauth2client", "uritemplate"}

def _get_ignore_callback(source_root):
    """
    ULTIMATE TIME: Pre-calculates path logic to ensure O(1) decision making.
    """
    source_root = Path(source_root).resolve()

    def ignore_func(path, names):
        current_path = Path(path).resolve()
        ignored = set()
        
        # Apply sample-specific ignores if we aren't in the root
        if current_path != source_root:
            ignored.update(IGNORE_IN_SAMPLES.intersection(names))
            
        # Apply global ignores
        ignored.update(IGNORE.intersection(names))
        return list(ignored)
        
    return ignore_func

def main(args):
    source = Path(args.source)
    dest = Path(args.dest)

    # SPACE: Remove existing destination to prevent merge conflicts
    if dest.exists():
        shutil.rmtree(dest)

    try:
        # ULTIMATE SPACE: symlinks=False expands (copies) the actual content
        # of the symlink rather than just copying the link itself.
        shutil.copytree(
            source, 
            dest, 
            symlinks=False, 
            ignore=_get_ignore_callback(source),
            dirs_exist_ok=True
        )
        print(f"Successfully created snapshot at: {dest}")
    except Exception as e:
        print(f"Error during snapshot creation: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Copy source to dest expanding symlinks and filtering internals."
    )
    parser.add_argument("--source", default=".", help="Source directory.")
    parser.add_argument("--dest", default="snapshot", help="Destination directory.")
    
    # Resolve 'FLAGS' issue by passing parsed args directly
    main(parser.parse_args())