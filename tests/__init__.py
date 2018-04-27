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

__author__ = 'afshar@google.com (Ali Afshar)'


from googleapiclient import _helpers as util


def setup_package():
  """Run on testing package."""
  util.positional_parameters_enforcement = 'EXCEPTION'
