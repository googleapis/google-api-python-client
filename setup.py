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

import setup_utils

packages = ['apiclient', 'apiclient.ext', 'uritemplate']

# Don't clobber installed versions of third party libraries
# with what we include.
packages.extend(setup_utils.get_missing_requirements())
print 'Installing the following packages: '
print str(packages)[1:-1]

try:
  # Some people prefer setuptools, and may have that installed
  from setuptools import setup
except ImportError:
  from distutils.core import setup
  print 'Loaded distutils.core'
else:
  print 'Loaded setuptools'

long_desc = """The Google API Client for Python is a client library for 
accessing the Buzz, Moderator, and Latitude APIs."""

setup(name="google-api-python-client",
      version="0.1",
      description="Google API Client Library for Python",
      long_description=long_desc,
      author="Joe Gregorio",
      author_email="jcgregorio@google.com",
      url="http://code.google.com/p/google-api-python-client/",
      packages=packages,
      package_data={'apiclient':['contrib/buzz/future.json',
                                 'contrib/latitude/future.json',
                                 'contrib/moderator/future.json']},
      license="Apache 2.0",
      keywords="google api client",
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Apache Software License',
                   'Operating System :: POSIX',
                   'Topic :: Internet :: WWW/HTTP'])

print 'Setup complete!'
