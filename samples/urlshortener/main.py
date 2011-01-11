#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
#
# Copyright 2010 Google Inc. All Rights Reserved.

"""Simple command-line example for Google URL Shortener API.

Command-line application that shortens a URL.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

from apiclient.discovery import build

import pprint

# Uncomment the next two lines to get very detailed logging
#import httplib2
#httplib2.debuglevel = 4


def main():

  # Build the url shortener service
  service = build("urlshortener", "v1",
            developerKey="AIzaSyDRRpR3GS1F1_jKNNM9HCNd2wJQyPG3oN0")
  url = service.url()

  # Create a shortened URL by inserting the URL into the url collection.
  body = {"longUrl": "http://code.google.com/apis/urlshortener/" }
  resp = url.insert(body=body).execute()
  pprint.pprint(resp)

  shortUrl = resp['id']

  # Convert the shortened URL back into a long URL
  resp = url.get(shortUrl=shortUrl).execute()
  pprint.pprint(resp)

if __name__ == '__main__':
  main()
