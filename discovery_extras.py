# Copyright (C) 2010 Google Inc.
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

"""Generate a skeleton discovery extras document.

For the given API, retrieve the discovery document,
strip out the guts of each method description
and put :
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import os
import os.path
import sys

from anyjson import simplejson


def main():
  for filename in sys.argv[1:]:
    f = file(filename, "r")
    dis = simplejson.load(f)
    f.close()

    api = dis['name']
    version = dis['version']
    resources = dis['resources']
    for res_name, res_desc in resources.iteritems():
      methods = res_desc['methods']
      for method_name, method_desc in methods.iteritems():
        methods[method_name] = {}
    path, basename = os.path.split(filename)
    newfilename = os.path.join(path, "skel-" + basename)
    f = file(newfilename, "w")
    simplejson.dump(dis, f, sort_keys=True, indent=2 * ' ')
    f.close()


if __name__ == '__main__':
  main()
