#!/usr/bin/env python
import glob
import imp
import logging
import os
import sys
import unittest
from trace import fullmodname

logging.basicConfig(level=logging.CRITICAL)

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


def main():
  for t in sys.argv[1:]:
    module = imp.load_source('test', t)
    test = unittest.TestLoader().loadTestsFromModule(module)
    result = unittest.TextTestRunner(verbosity=1).run(test)


if __name__ == '__main__':
  main()
