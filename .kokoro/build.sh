#!/bin/bash

set -eo pipefail

cd github/google-api-python-client

# Disable buffering, so that the logs stream through.
export PYTHONUNBUFFERED=1

pip install tox coveralls

# Run tests
tox

coveralls
