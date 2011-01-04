#!/usr/bin/python2.4
#
# Copyright 2010 Google Inc. All Rights Reserved.

"""Errors for the library.

All exceptions defined by the library
should be defined in this file.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'


from anyjson import simplejson


class Error(Exception):
  """Base error for this module."""
  pass


class HttpError(Error):
  """HTTP data was invalid or unexpected."""

  def __init__(self, resp, content):
    self.resp = resp
    self.content = content

  def _get_reason(self):
    """Calculate the reason for the error from the response content.
    """
    if self.resp.get('content-type', '').startswith('application/json'):
      try:
        data = simplejson.loads(self.content)
        reason = data['error']['message']
      except (ValueError, KeyError):
        reason = self.content
    else:
      reason = self.resp.reason
    return reason

  def __repr__(self):
    return '<HttpError %s "%s">' % (self.resp.status, self._get_reason())

  __str__ = __repr__


class UnknownLinkType(Error):
  """Link type unknown or unexpected."""
  pass
