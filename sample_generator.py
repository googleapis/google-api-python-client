#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
#
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

"""Generate command-line samples from stubs.

Generates a command-line client sample application from a set of files
that contain only the relevant portions that change between each API.
This allows all the common code to go into a template.

Usage:
  python sample_generator.py

Must be run from the root of the respository directory.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import os.path
import glob
import sys
import pprint
import string
import textwrap

if not os.path.isdir('samples/src'):
  sys.exit('Must be run from root of the respository directory.')

f = open('samples/src/template.tmpl', 'r')
template = string.Template(f.read())
f.close()

for filename in glob.glob('samples/src/*.py'):
  # Create a dictionary from the config file to later use in filling in the
  # templates.
  f = open(filename, 'r')
  contents = f.read()
  f.close()
  config, content = contents.split('\n\n', 1)
  variables = {}
  for line in config.split('\n'):
    key, value = line[1:].split(':', 1)
    variables[key.strip()] = value.strip()

  lines = content.split('\n')
  outlines = []
  for l in lines:
    if l:
      outlines.append('  ' + l)
    else:
      outlines.append('')
  content = '\n'.join(outlines)

  variables['description'] = textwrap.fill(variables['description'])
  variables['content'] = content
  variables['name'] = os.path.basename(filename).split('.', 1)[0]

  f = open(os.path.join('samples', variables['name'], variables['name'] + '.py'), 'w')
  f.write(template.substitute(variables))
  f.close()
  print 'Processed: %s' % variables['name']
