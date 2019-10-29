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

if sys.version_info < (2, 7):
  print('google-api-python-client requires python version >= 2.7.',
        file=sys.stderr)
  sys.exit(1)
if (3, 1) <= sys.version_info < (3, 4):
  print('google-api-python-client requires python3 version >= 3.4.',
        file=sys.stderr)
  sys.exit(1)

from setuptools import setup

packages = [
    'apiclient',
    'googleapiclient',
    'googleapiclient/discovery_cache',
]

install_requires = [
    'httplib2>=0.9.2,<1dev',
    'google-auth>=1.4.1',
    'google-auth-httplib2>=0.0.3',
    'six>=1.6.1,<2dev',
    'uritemplate>=3.0.0,<4dev',
]

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
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*',
    packages=packages,
    package_data={},
    license="Apache 2.0",
    keywords="google api client",
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
