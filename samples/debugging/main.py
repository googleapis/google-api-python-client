#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
#
# Copyright 2010 Google Inc. All Rights Reserved.

"""Simple command-line example for Translate.

Command-line application that translates
some text.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import gflags
import logging
import pprint
import sys

from apiclient.discovery import build
from apiclient.model import LoggingJsonModel


FLAGS = gflags.FLAGS
FLAGS.dump_request_response = True
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def main(argv):
  service = build('translate', 'v2',
                  developerKey='AIzaSyAQIKv_gwnob-YNrXV2stnY86GSGY81Zr0',
                  model=LoggingJsonModel())
  print service.translations().list(
      source='en',
      target='fr',
      q=['flower', 'car']
    ).execute()

if __name__ == '__main__':
  main(sys.argv)
