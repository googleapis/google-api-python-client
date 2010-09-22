#!/usr/bin/env python
import glob
import logging
import os
import sys
import unittest

from trace import fullmodname
try:
    from tests.utils import cleanup
except:
    def cleanup():
        pass

sys.path.insert(0, os.getcwd())

verbosity = 1
if "-q" in sys.argv or '--quiet' in sys.argv:
    verbosity = 0
if "-v" in sys.argv or '--verbose' in sys.argv:
    verbosity = 2

if verbosity == 0:
  logging.disable(logging.CRITICAL)
elif verbosity == 1:
  logging.disable(logging.ERROR)
elif verbosity == 2:
  logging.basicConfig(level=logging.DEBUG)


def build_suite(folder):
  # find all of the test modules
  modules = map(fullmodname, glob.glob(os.path.join(folder, 'test_*.py')))
  if verbosity > 0:
    print "Running the tests found in the following modules:"
    print modules

  # load all of the tests into a suite
  try:
      return unittest.TestLoader().loadTestsFromNames(modules)
  except Exception, exception:
      # attempt to produce a more specific message
      for module in modules:
          __import__(module)
      raise

# build and run unit test suite
unit_tests = build_suite('tests')
unittest.TextTestRunner(verbosity=verbosity).run(unit_tests)
cleanup()

# build and run functional test suite
functional_tests = build_suite('functional_tests')
unittest.TextTestRunner(verbosity=verbosity).run(functional_tests)
cleanup()
