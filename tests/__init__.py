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

"""Test Package set up."""
from __future__ import absolute_import

__author__ = "afshar@google.com (Ali Afshar)"


from googleapiclient import _helpers as util

# The test suite is written against strict positional parameter enforcement:
# violations must raise TypeError rather than only log a warning. This used to
# be configured in a nose-era setup_package() hook, which pytest never calls,
# so set it at import time instead.
util.positional_parameters_enforcement = util.POSITIONAL_EXCEPTION
