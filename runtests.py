#!/usr/bin/env python
import glob
import logging
import os
import sys
import unittest
from trace import fullmodname

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


def build_suite(folder, verbosity):
  # find all of the test modules
  top_level_modules = map(fullmodname, glob.glob(os.path.join(folder, 'test_*.py')))
  # TODO(ade) Verify that this works on Windows. If it doesn't then switch to os.walk instead
  lower_level_modules = map(fullmodname, glob.glob(os.path.join(folder, '*/test_*.py')))
  modules = top_level_modules + lower_level_modules
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

def run(test_folder_name, verbosity, exit_on_failure):
  # Build and run the tests in test_folder_name
  tests = build_suite(test_folder_name, verbosity)
  result = unittest.TextTestRunner(verbosity=verbosity).run(tests)
  if exit_on_failure and not result.wasSuccessful():
    sys.exit(1)
  cleanup()

def main():
  if '--help' in sys.argv:
    print 'Usage: python runtests.py [-q|--quiet|-v|--verbose] [--exit_on_failure] [tests|functional_tests|contrib_tests]'
    return
  verbosity = 1
  exit_on_failure = '--exit_on_failure' in sys.argv
  if '-q' in sys.argv or '--quiet' in sys.argv:
    verbosity = 0
  if "-v" in sys.argv or '--verbose' in sys.argv:
    verbosity = 2
  if verbosity == 0:
    logging.disable(logging.CRITICAL)
  elif verbosity == 1:
    logging.disable(logging.ERROR)
  elif verbosity == 2:
    logging.basicConfig(level=logging.DEBUG)

  import dev_appserver
  dev_appserver.fix_sys_path()
  # Allow user to run a specific folder of tests
  if 'tests' in sys.argv:
    run('tests', verbosity, exit_on_failure)
  elif 'functional_tests' in sys.argv:
    run('functional_tests', verbosity, exit_on_failure)
  elif 'contrib_tests' in sys.argv:
    run('contrib_tests', verbosity, exit_on_failure)
  else:
    run('tests', verbosity, exit_on_failure)
    run('functional_tests', verbosity, exit_on_failure)
    run('contrib_tests', verbosity, exit_on_failure)

if __name__ == '__main__':
  main()
