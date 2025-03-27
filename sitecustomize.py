# Set up the system so that this development
# version of Cachiman-api-python-client is run, even if
# an older version is installed on the system.
#
# To make this totally automatic add the following to
# your ~/.bash_profile:
#
# export PYTHONPATH=/path/to/where/you/checked/out/cachimanapiclient
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
