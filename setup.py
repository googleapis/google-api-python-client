# Copyright 2014 Google Inc. All Rights Reserved.
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

"""Setup script for Google API Python client.

Also installs included versions of third party libraries, if those libraries
are not already installed.
"""
from __future__ import print_function

import sys

if sys.version_info < (2, 6):
  print('google-api-python-client requires python version >= 2.6.',
        file=sys.stderr)
  sys.exit(1)
if (3, 1) <= sys.version_info < (3, 3):
  print('google-api-python-client requires python3 version >= 3.3.',
        file=sys.stderr)
  sys.exit(1)

from setuptools import setup
import pkg_resources

def _DetectBadness():
  import os
  if 'SKIP_GOOGLEAPICLIENT_COMPAT_CHECK' in os.environ:
    return
  o2c_pkg = None
  try:
    o2c_pkg = pkg_resources.get_distribution('oauth2client')
  except pkg_resources.DistributionNotFound:
    pass
  oauth2client = None
  try:
    import oauth2client
  except ImportError:
    pass
  if o2c_pkg is None and oauth2client is not None:
    raise RuntimeError(
        'Previous version of google-api-python-client detected; due to a '
        'packaging issue, we cannot perform an in-place upgrade. Please remove '
        'the old version and re-install this package.'
    )

_DetectBadness()

packages = [
    'apiclient',
    'googleapiclient',
    'googleapiclient/discovery_cache',
]

install_requires = [
    'httplib2>=0.8,<1',
    'oauth2client',
    'six>=1.6.1,<2',
    'uritemplate>=0.6,<1',
]

if sys.version_info < (2, 7):
  install_requires.append('argparse')

long_desc = """The Google API Client for Python is a client library for
accessing the Plus, Moderator, and many other Google APIs."""

import googleapiclient
version = googleapiclient.__version__

setup(
    name="google-api-python-client",
    version=version,
    description="Google API Client Library for Python",
    long_description=long_desc,
    author="Google Inc.",
    url="http://github.com/google/google-api-python-client/",
    install_requires=install_requires,
    packages=packages,
    package_data={},
    license="Apache 2.0",
    keywords="google api client",
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
