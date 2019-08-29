#!/bin/bash

set -eo pipefail

# Start the releasetool reporter
python3 -m pip install gcp-releasetool
python3 -m releasetool publish-reporter-script > /tmp/publisher-script; source /tmp/publisher-script

# Ensure that we have the latest versions of Twine, Wheel, and Setuptools.
python3 -m pip install --upgrade twine wheel setuptools

# Disable buffering, so that the logs stream through.
export PYTHONUNBUFFERED=1

# Move into the package, build the distribution and upload.
TWINE_PASSWORD=$(cat "${KOKORO_KEYSTORE_DIR}/73713_google_cloud_pypi_password")
cd github/google-api-python-client
python3 setup.py sdist bdist_wheel
twine upload --username gcloudpypi --password "${TWINE_PASSWORD}" dist/*
