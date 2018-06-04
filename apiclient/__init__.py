"""Retain apiclient as an alias for googleapiclient."""

from six import iteritems

import googleapiclient

from googleapiclient import channel
from googleapiclient import discovery
from googleapiclient import errors
from googleapiclient import http
from googleapiclient import mimeparse
from googleapiclient import model
from googleapiclient import sample_tools
from googleapiclient import schema

__version__ = googleapiclient.__version__

_SUBMODULES = {
    'channel': channel,
    'discovery': discovery,
    'errors': errors,
    'http': http,
    'mimeparse': mimeparse,
    'model': model,
    'sample_tools': sample_tools,
    'schema': schema,
}

import sys
for module_name, module in iteritems(_SUBMODULES):
  sys.modules['apiclient.%s' % module_name] = module
