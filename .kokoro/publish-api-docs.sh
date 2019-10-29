#!/bin/bash

# set -eo pipefail

# Disable buffering, so that the logs stream through.
export PYTHONUNBUFFERED=1

cd github/google-api-python-client

# Install library
python3 -m pip install --user .

# Install docuploader
python3 -m pip install --user gcp-docuploader

# Serve docs at https://googleapis.dev/python/google-api-python-client/latest/api-docs
# Index page at https://googleapis.dev/python/google-api-python-client/latest/api-docs/index.html
# Only the latest version is served since the client is generated at runtime.
DESTINATION='api_docs'
METADATA_PATH=${DESTINATION}/docs.metadata
SERVING_PATH='python/google-api-python-client/latest/api-docs'
VERSION='latest'

# Run script
python3 describe.py --dest ${DESTINATION}

# create docs metadata
python3 -m docuploader create-metadata \
  --name=$(jq --raw-output '.name // empty' .repo-metadata.json) \
  --language=$(jq --raw-output '.language // empty' .repo-metadata.json) \
  --distribution-name=$(python3 setup.py --name) \
  --version ${VERSION} \
  --github-repository=$(jq --raw-output '.repo // empty' .repo-metadata.json) \
  --issue-tracker=$(jq --raw-output '.issue_tracker // empty' .repo-metadata.json) \
  --serving-path=${SERVING_PATH} \
  ${METADATA_PATH}

cat ${METADATA_PATH}

# # upload docs
python3 -m docuploader upload api_docs --metadata-file docs.metadata --staging-bucket busun-sandbox
