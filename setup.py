#!/usr/bin/env python
from distutils.core import setup

# First pass at a setup.py, in the long run we will
# need two, one for a version of the library that just
# includes apiclient, and another that also includes 
# all of the dependencies.
setup(name="google-api-python-client",
      version="0.1",
      description="Google API Client Library for Python",
      author="Joe Gregorio",
      author_email="jcgregorio@google.com",
      url="http://code.google.com/p/google-api-python-client/",
      py_modules = ['apiclient', 'oauth2', 'simplejson', 'uritemplate'],
      license = "Apache 2.0",
      keywords="google api client")
