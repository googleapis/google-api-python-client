#!/usr/bin/python2.4
#
# Copyright 2010 Google Inc. All Rights Reserved.

"""Errors for the library.

All exceptions defined by the library
should be defined in this file.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'


class Error(Exception):
  """Base error for this module."""
  pass


class HttpError(Error):
  """HTTP data was invalid or unexpected."""

  def __init__(self, resp, detail):
    self.resp = resp
    self.detail = detail

  def __str__(self):
    return self.detail


class UnknownLinkType(Error):
  """Link type unknown or unexpected."""
  pass
