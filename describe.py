#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
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

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import os
import pydoc
import re
import sys
import httplib2

from apiclient.anyjson import simplejson
from apiclient.discovery import build

BASE = 'docs/dyn'

def document(resource, path):
  print path
  collections = []
  for name in dir(resource):
    if not "_" in name and callable(getattr(resource, name)) and hasattr(
          getattr(resource, name), '__is_resource__'):
      collections.append(name)

  obj, name = pydoc.resolve(type(resource))
  page = pydoc.html.page(
      pydoc.describe(obj), pydoc.html.document(obj, name))

  for name in collections:
    page = re.sub('strong>(%s)<' % name, r'strong><a href="%s">\1</a><' % (path + name + ".html"), page)
  for name in collections:
    document(getattr(resource, name)(), path + name + ".")

  f = open(os.path.join(BASE, path + 'html'), 'w')
  f.write(page)
  f.close()

def document_api(name, version):
  service = build(name, version)
  document(service, '%s.%s.' % (name, version))

if __name__ == '__main__':
  http = httplib2.Http()
  resp, content = http.request('https://www.googleapis.com/discovery/v0.3/directory?preferred=true')
  if resp.status == 200:
    directory = simplejson.loads(content)['items']
    for api in directory:
      document_api(api['name'], api['version'])
  else:
    sys.exit("Failed to load the discovery document.")
