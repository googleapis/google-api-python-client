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

has_setuptools = False
try:
  from setuptools import setup
  has_setuptools = True
except ImportError:
  from distutils.core import setup

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

install_requires = []
py_modules = []


# (module to test for, install_requires to add if missing, packages to add if missing, py_modules to add if missing)
REQUIREMENTS = [
  ('httplib2', 'httplib2', 'httplib2', None),
  ('oauth2', 'oauth2', 'oauth2', None),
  ('gflags', 'python-gflags', None, ['gflags', 'gflags_validators']),
  (['json', 'simplejson', 'django.utils'], 'simplejson', 'simplejson', None)
]

for import_name, requires, package, modules in REQUIREMENTS:
  if setup_utils.is_missing(import_name):
    if has_setuptools:
      install_requires.append(requires)
    else:
      if package is not None:
        packages.append(package)
      else:
        py_modules.extend(modules)


long_desc = """The Google API Client for Python is a client library for
accessing the Buzz, Moderator, and Latitude APIs."""

setup(name="google-api-python-client",
      version="1.0beta2",
      description="Google API Client Library for Python",
      long_description=long_desc,
      author="Joe Gregorio",
      author_email="jcgregorio@google.com",
      url="http://code.google.com/p/google-api-python-client/",
      install_requires=install_requires,
      packages=packages,
      py_modules=py_modules,
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
