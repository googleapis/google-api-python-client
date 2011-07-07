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

"""Setup script for oauth2client.

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
  'oauth2client',
]

install_requires = []
py_modules = []


# (module to test for, install_requires to add if missing, packages to add if missing, py_modules to add if missing)
REQUIREMENTS = [
  ('httplib2', 'httplib2', 'httplib2', None),
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


long_desc = """The oauth2client is a client library for OAuth 2.0."""

setup(name="oauth2client",
      version="1.0beta2",
      description="OAuth 2.0 client library",
      long_description=long_desc,
      author="Joe Gregorio",
      author_email="jcgregorio@google.com",
      url="http://code.google.com/p/google-api-python-client/",
      install_requires=install_requires,
      packages=packages,
      py_modules=py_modules,
      license="Apache 2.0",
      keywords="google oauth 2.0 http client",
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Apache Software License',
                   'Operating System :: POSIX',
                   'Topic :: Internet :: WWW/HTTP'])
