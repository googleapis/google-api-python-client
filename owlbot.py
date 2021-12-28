# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import synthtool as s
from synthtool import gcp

from synthtool.languages import python

common = gcp.CommonTemplates()

# ----------------------------------------------------------------------------
# Add templated files
# ----------------------------------------------------------------------------
templated_files = common.py_library()

# Copy kokoro configs.
# Docs are excluded as repo docs cannot currently be generated using sphinx.
s.move(templated_files / '.kokoro', excludes=['**/docs/*', 'publish-docs.sh'])
s.move(templated_files / '.trampolinerc')  # config file for trampoline_v2

# Also move issue templates
s.move(templated_files / '.github', excludes=['CODEOWNERS'])

# Move scripts folder needed for samples CI
s.move(templated_files / 'scripts')

# Copy CONTRIBUTING.rst
s.move(templated_files / 'CONTRIBUTING.rst')

# ----------------------------------------------------------------------------
# Samples templates
# ----------------------------------------------------------------------------

python.py_samples(skip_readmes=True)
