#!/bin/bash

set -eo pipefail

# Disable buffering, so that the logs stream through.
export PYTHONUNBUFFERED=1

cd github/google-api-python-client

# Remove old nox
python3.6 -m pip uninstall --yes --quiet nox-automation

# Install nox
python3.6 -m pip install --upgrade --quiet nox
python3.6 -m nox --version

# build docs
nox -s docs

python3 -m pip install gcp-docuploader

# install a json parser
sudo apt-get update
sudo apt-get -y install software-properties-common
sudo add-apt-repository universe
sudo apt-get update
sudo apt-get -y install jq

# create metadata
python3 -m docuploader create-metadata \
  --name=$(jq --raw-output '.name // empty' .repo-metadata.json) \
  --version=$(python3 setup.py --version) \
  --language=$(jq --raw-output '.language // empty' .repo-metadata.json) \
  --distribution-name=$(python3 setup.py --name) \
  --product-page=$(jq --raw-output '.product_documentation // empty' .repo-metadata.json) \
  --github-repository=$(jq --raw-output '.repo // empty' .repo-metadata.json) \
  --issue-tracker=$(jq --raw-output '.issue_tracker // empty' .repo-metadata.json)

cat docs.metadata

# upload docs
python3 -m docuploader upload docs/_build/html --metadata-file docs.metadata --staging-bucket docs-staging
