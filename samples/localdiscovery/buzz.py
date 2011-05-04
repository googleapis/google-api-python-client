#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
#
# Copyright 2010 Google Inc. All Rights Reserved.

"""Simple command-line example for Buzz.

Command-line application that retrieves the users
latest content and then adds a new entry.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

from apiclient.discovery import build_from_document

import httplib2
import os
import pprint

def main():
  http = httplib2.Http()

  # Load the local copy of the discovery document
  f = file(os.path.join(os.path.dirname(__file__), "buzz.json"), "r")
  discovery = f.read()
  f.close()

  # Optionally load a futures discovery document
  f = file(os.path.join(os.path.dirname(__file__), "../../apiclient/contrib/buzz/future.json"), "r")
  future = f.read()
  f.close()

  # Construct a service from the local documents
  service = build_from_document(discovery,
      base="https://www.googleapis.com/",
      http=http,
      future=future)

  pprint.pprint(service.activities().search(q='lady gaga').execute())


if __name__ == '__main__':
  main()
