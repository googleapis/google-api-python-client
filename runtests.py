#!/usr/bin/env python
import gflags
import glob
import imp
import logging
import os
import sys
import unittest

# import oauth2client.util for its gflags.
import oauth2client.util

from trace import fullmodname

logging.basicConfig(level=logging.CRITICAL)

FLAGS = gflags.FLAGS

APP_ENGINE_PATH='../google_appengine'

# Conditional import of cleanup function
try:
  from tests.utils import cleanup
except:
  def cleanup():
    pass

# Ensure current working directory is in path
sys.path.insert(0, os.getcwd())
sys.path.insert(0, APP_ENGINE_PATH)

from google.appengine.dist import use_library
use_library('django', '1.2')


def main(argv):
  argv = FLAGS(argv)
  for t in argv[1:]:
    module = imp.load_source('test', t)
    test = unittest.TestLoader().loadTestsFromModule(module)
    result = unittest.TextTestRunner(verbosity=1).run(test)


if __name__ == '__main__':
  main(sys.argv)
