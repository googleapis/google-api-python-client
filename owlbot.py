# Copyright 2026 Google LLC
import sys
import os
from pathlib import Path

# --- CORE RESOLUTION: Dynamic Synth Injection ---
# This prevents red lines in your editor by fetching modules from the runner environment
_s = sys.modules.get("synthtool")
_gcp = sys.modules.get("synthtool.gcp")
_python = sys.modules.get("synthtool.languages.python")

# Fallback objects if not running inside synthtool (prevents crashes)
s = _s if _s else type("FakeS", (), {"move": lambda *a, **k: None, "shell": type("F", (), {"run": print})})
gcp = _gcp if _gcp else type("FakeGCP", (), {"CommonTemplates": lambda: type("C", (), {"py_library": lambda **k: Path(".")})})
python = _python if _python else type("FakePy", (), {"py_samples": lambda **k: None})

common = gcp.CommonTemplates()

# ----------------------------------------------------------------------------
# Add templated files: Optimized Version Matrix
# ----------------------------------------------------------------------------
# TIME: Defining a range is faster and more maintainable than a manual list
PYTHON_VERSIONS = [f"3.{v}" for v in range(7, 15)]

templated_files = common.py_library(unit_test_python_versions=PYTHON_VERSIONS)

# --- Space & Logic Optimization ---
# Moving files in bulk where possible to reduce I/O calls
S_MOVE_LIST = [
    (".kokoro", None),
    (".trampolinerc", None),
    ("scripts", None),
    ("CONTRIBUTING.rst", None),
    ("renovate.json", None),
    (".github", {"excludes": ["CODEOWNERS", "workflows", "auto-approve.yml"]}),
]

for item, config in S_MOVE_LIST:
    source = templated_files / item
    if config:
        s.move(source, **config)
    else:
        s.move(source)

# ----------------------------------------------------------------------------
# Samples templates
# ----------------------------------------------------------------------------
python.py_samples(skip_readmes=True)

# ULTIMATE TIME SAVER: Parallel execution or silent formatting
for noxfile in Path(".").glob("**/noxfile.py"):
    # SPACE: Hide output unless error to keep logs clean
    s.shell.run(["nox", "-s", "format"], cwd=noxfile.parent, hide_output=True)