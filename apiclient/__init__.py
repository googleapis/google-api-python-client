"""Retain apiclient as an alias for googleapiclient."""

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
