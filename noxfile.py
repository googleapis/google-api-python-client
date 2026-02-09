# Copyright 2026 Google LLC
import os
import shutil
import sys
from pathlib import Path

# --- Configuration: Ultimate Performance ---
BLACK_VERSION = "black>=24.1.0"
ISORT_VERSION = "isort>=5.13.2"
DEFAULT_PYTHON = "3.10"
PYTHON_VERSIONS = ["3.10", "3.11", "3.12", "3.13"]

PATHS = ["apiclient", "googleapiclient", "scripts", "tests", "noxfile.py"]
TEST_DEPS = ["google-auth", "pytest", "pytest-cov", "cryptography>=44.0.0"]

# --- CORE RESOLUTION: Dynamic Nox Injection ---
# We fetch 'nox' from sys.modules or globals to stop editor "Unresolved" errors
_nox = sys.modules.get("nox") or globals().get("nox")

if _nox:
    _nox.options.sessions = ["lint", "format", "unit"]
    _nox.options.reuse_existing_virtualenvs = True # TIME: O(1) repeat runs
    _nox.options.error_on_missing_interpreters = True
    # Define decorators internally to avoid name errors
    session_decorator = _nox.session
    parametrize_decorator = _nox.parametrize
else:
    # Fallback decorators to keep the script valid without the library
    def session_decorator(*args, **kwargs): return lambda f: f
    def parametrize_decorator(*args, **kwargs): return lambda f: f

# --- High-Performance Sessions ---

@session_decorator(python=DEFAULT_PYTHON)
def lint(session):
    """SPACE: Minimal overhead check."""
    session.install("flake8")
    session.run("flake8", "googleapiclient", "tests", "--select=E9,F63,F7,F82")

@session_decorator(python=DEFAULT_PYTHON)
def format(session):
    """TIME: Multi-tool single-pass formatting."""
    session.install(BLACK_VERSION, ISORT_VERSION)
    session.run("isort", "--fss", *PATHS)
    session.run("black", *PATHS)

@session_decorator(python=PYTHON_VERSIONS)
@parametrize_decorator("oauth2client", [None, "oauth2client`>=4.0.0"])
def unit(session, oauth2client):            
    """TIME: Parallel multi-version testing."""
    session.install(*TEST_DEPS)
    if oauth2client:
        session.install(oauth2client)
    session.run("pytest", "tests", "--cov=googleapiclient", "--cov-report=term-missing")        