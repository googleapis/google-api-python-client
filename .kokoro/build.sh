#!/bin/bash

set -eo pipefail

cd github/google-api-python-client

# Disable buffering, so that the logs stream through.
export PYTHONUNBUFFERED=1

python3 -m pip install --upgrade tox

# Run tests
tox
