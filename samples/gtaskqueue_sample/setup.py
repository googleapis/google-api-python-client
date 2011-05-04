#!/usr/bin/env python
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

"""Setup script for the Google TaskQueue API command-line tool."""

__version__ = '1.0.2'


import sys
try:
    from setuptools import setup
    print 'Loaded setuptools'
except ImportError:
    from distutils.core import setup
    print 'Loaded distutils.core'


PACKAGE_NAME = 'google-taskqueue-client'
INSTALL_REQUIRES = ['google-apputils==0.1',
                    'google-api-python-client',
                    'httplib2',
                    'oauth2',
                    'python-gflags']
setup(name=PACKAGE_NAME,
      version=__version__,
      description='Google TaskQueue API command-line tool and utils',
      author='Google Inc.',
      author_email='google-appengine@googlegroups.com',
      url='http://code.google.com/appengine/docs/python/taskqueue/pull/overview.html',
      install_requires=INSTALL_REQUIRES,
      packages=['gtaskqueue'],
      scripts=['gtaskqueue/gtaskqueue', 'gtaskqueue/gtaskqueue_puller',
               'gtaskqueue/gen_appengine_access_token'],
      license='Apache 2.0',
      keywords='google taskqueue api client',
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Apache Software License',
                   'Operating System :: POSIX',
                   'Topic :: Internet :: WWW/HTTP'])
