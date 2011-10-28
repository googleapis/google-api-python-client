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

"""Setup script for Google API Python client.

Also installs included versions of third party libraries, if those libraries
are not already installed.
"""
from setuptools import setup

packages = [
  'apiclient',
  'oauth2client',
  'apiclient.ext',
  'apiclient.contrib',
  'apiclient.contrib.buzz',
  'apiclient.contrib.latitude',
  'apiclient.contrib.moderator',
  'uritemplate',
  ]

install_requires = [
    'httplib2',
    'oauth2',
    'python-gflags',
    ]

try:
  import json
  needs_json = False
except ImportError:
  needs_json = True

if needs_json:
  install_requires.append('simplejson')

long_desc = """The Google API Client for Python is a client library for
accessing the Buzz, Moderator, and Latitude APIs."""

setup(name="google-api-python-client",
      version="1.0beta6",
      description="Google API Client Library for Python",
      long_description=long_desc,
      author="Joe Gregorio",
      author_email="jcgregorio@google.com",
      url="http://code.google.com/p/google-api-python-client/",
      install_requires=install_requires,
      packages=packages,
      package_data={
        'apiclient': ['contrib/*/*.json']
        },
      scripts=['bin/enable-app-engine-project'],
      license="Apache 2.0",
      keywords="google api client",
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Apache Software License',
                   'Operating System :: POSIX',
                   'Topic :: Internet :: WWW/HTTP'])
