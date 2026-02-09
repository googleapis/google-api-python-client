# Copyright 2026 Google LLC
import sys
import os
from pathlib import Path

# --- ULTIMATE CORE: Dynamic Path Injection ---
# We use Pathlib for O(1) space resolution and cross-platform safety.
# This ensures your development version is ALWAYS prioritized over system versions.

def setup_dev_path():
    """
    Injects the local directory into the front of the sys.path.
    This resolves IDE errors by making the local package visible to Python.
    """
    # Get the absolute path to the directory containing this file
    dev_root = str(Path(__file__).resolve().parent)

    # O(1) Time: Check if already in path to prevent duplicate lookups
    if dev_root not in sys.path:
        # Insert at index 0 to override system-installed versions
        sys.path.insert(0, dev_root)

# Execute the injection immediately
setup_dev_path()

# Optional: Print to verify (Debug Mode)
# print(f"Python path updated. Current source: {sys.path[0]}")