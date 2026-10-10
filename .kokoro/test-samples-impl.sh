#!/bin/bash
# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -eo pipefail
shopt -s globstar

# Exit early if samples don't exist
if ! find samples -name 'requirements.txt' | grep -q .; then
  echo "No tests run. './samples/**/requirements.txt' not found"
  exit 0
fi

# Disable buffering, so that the logs stream through.
export PYTHONUNBUFFERED=1

# Debug: show build environment
env | grep KOKORO

# Install nox

# Setup project id.
if [[ -f "${KOKORO_GFILE_DIR}/project-id.json" ]]; then
  export PROJECT_ID=$(cat "${KOKORO_GFILE_DIR}/project-id.json")
  export GOOGLE_CLOUD_PROJECT="${PROJECT_ID}"
  gcloud config set project "$PROJECT_ID"
  
  # Compute tests require CLOUD_STORAGE_BUCKET. We reuse a fixed bucket name
  # within the project so it doesn't leak thousands of buckets over time.
  export CLOUD_STORAGE_BUCKET="${PROJECT_ID}-api-client-compute"
fi

# Setup service account credentials.
if [[ -f "${KOKORO_GFILE_DIR}/service-account.json" ]]; then
  export GOOGLE_APPLICATION_CREDENTIALS="${KOKORO_GFILE_DIR}/service-account.json"
  gcloud auth activate-service-account --key-file="${GOOGLE_APPLICATION_CREDENTIALS}"
fi

echo -e "\n******************** TESTING PROJECTS ********************"

set +e
RTN=0
ROOT=$(pwd)
# Find all requirements.txt in the samples directory (may break on whitespace).
for file in samples/**/requirements.txt; do
    cd "$ROOT"
    file=$(dirname "$file")
    cd "$file"

    echo "------------------------------------------------------------"
    echo "- testing $file"
    echo "------------------------------------------------------------"

    python3 -m nox -s "$RUN_TESTS_SESSION"
    EXIT=$?

    if [[ $KOKORO_BUILD_ARTIFACTS_SUBDIR = *"periodic"* ]]; then
      chmod +x $KOKORO_GFILE_DIR/linux_amd64/flakybot
      $KOKORO_GFILE_DIR/linux_amd64/flakybot
    fi

    if [[ $EXIT -ne 0 ]]; then
      RTN=1
      echo -e "\n Testing failed: Nox returned a non-zero exit code. \n"
    else
      echo -e "\n Testing completed.\n"
    fi
done

cd "$ROOT"
exit "$RTN"
