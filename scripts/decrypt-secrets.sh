#!/bin/bash

# Copyright 2015 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT=$( dirname "$DIR" )

# Work from the project root.
cd $ROOT

# Prevent it from overriding files.
# We recommend that sample authors use their own service account files and cloud project.
# In that case, they are supposed to prepare these files by themselves.
if [[ -f "testing/test-env.sh" ]] || \
       [[ -f "testing/service-account.json" ]] || \
       [[ -f "testing/client-secrets.json" ]]; then
    echo "One or more target files exist, aborting."
    exit 1
fi

# Use SECRET_MANAGER_PROJECT if set, fallback to cloud-devrel-kokoro-resources.
PROJECT_ID="${SECRET_MANAGER_PROJECT:-cloud-devrel-kokoro-resources}"

gcloud secrets versions access latest --secret="python-docs-samples-test-env" \
       --project="${PROJECT_ID}" \
       > testing/test-env.sh
gcloud secrets versions access latest \
       --secret="python-docs-samples-service-account" \
       --project="${PROJECT_ID}" \
       > testing/service-account.json
gcloud secrets versions access latest \
       --secret="python-docs-samples-client-secrets" \
       --project="${PROJECT_ID}" \
       > testing/client-secrets.json
