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

"""Utility functions for setup.py file(s)."""


__author__ = 'tom.h.miller@gmail.com (Tom Miller)'


def get_missing_requirements():
  """Return a list of missing third party packages."""
  import sys

  sys_path_original = sys.path[:]
  # Remove the current directory from the list of paths to check when
  # importing modules.
  try:
    # Sometimes it's represented by an empty string?
    sys.path.remove('')
  except ValueError:
    import os.path
    sys.path.remove(os.path.abspath(os.path.curdir))
  missing_pkgs = []
  third_party_reqs = ['oauth2', 'httplib2']
  for pkg in third_party_reqs:
    try:
      __import__(pkg)
    except ImportError:
      missing_pkgs.append(pkg)
  # JSON support gets its own special logic
  try:
    import_json(sys.path)
  except ImportError:
    missing_pkgs.append('simplejson')

  sys.path = sys_path_original
  return missing_pkgs


def import_json(import_path=None):
  """Return a package that will provide JSON support.

  Args:
    import_path: list Value to assing to sys.path before checking for packages.
                 Default None for default sys.path.
  Return:
    A package, one of 'json' (if running python 2.6),
                      'django.utils.simplejson' (if django is installed)
                      'simplejson' (if third party library simplejson is found)
  Raises:
    ImportError if none of those packages are found.
  """
  import sys
  sys_path_orig = sys.path[:]
  if import_path is not None:
    sys.path = import_path

  try:
    # Should work for Python 2.6.
    pkg = __import__('json')
  except ImportError:
    try:
      pkg = __import__('django.utils').simplejson
    except ImportError:
      try:
        pkg = __import__('simplejson')
      except ImportError:
        pkg = None

  if import_path is not None:
    sys.path = sys_path_orig
  if pkg:
    return pkg
  else:
    raise ImportError('Cannot find json support')    
