#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Google Inc.

"""Sample for retrieving advertiser information from GAN."""

__author__ = 'leadpipe@google.com (Luke Blanshard)'

import apiclient
import gflags
import httplib2
import json
import logging
import os
import stat
import sys

from django.conf import settings
from django.template import Template, Context
from django.template.loader import get_template

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run

settings.configure(DEBUG=True, TEMPLATE_DEBUG=True,
    TEMPLATE_DIRS=('.'))


FLAGS = gflags.FLAGS

# CLIENT_SECRETS, name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret, which are found
# on the API Access tab on the Google APIs
# Console <http://code.google.com/apis/console>
CLIENT_SECRETS = '../client_secrets.json'

# Helpful message to display in the browser if the CLIENT_SECRETS file
# is missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the APIs Console <https://code.google.com/apis/console>.

""" % os.path.join(os.path.dirname(__file__), CLIENT_SECRETS)

# Set up a Flow object to be used if we need to authenticate.
FLOW = flow_from_clientsecrets(CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/gan.readonly',
    message=MISSING_CLIENT_SECRETS_MESSAGE)


# The gflags module makes defining command-line options easy for
# applications. Run this program with the '--help' argument to see
# all the flags that it understands.
gflags.DEFINE_enum('logging_level', 'DEBUG',
    ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    'Set the level of logging detail.')

gflags.DEFINE_enum("request_type", 'LIST', ['GET', 'LIST'],
                   'Type of request to be made')

gflags.DEFINE_enum("output_type", 'STDOUT', ['BOTH', 'HTML', 'STDOUT'],
                   'Set how to output the results received from the API')

gflags.DEFINE_string('credentials_filename', '../credentials.dat',
                     'File to store credentials in', short_name='cf')

API_FLAGS = {'relationshipStatus':None, 'advertiserId':None, 'role':None,
             'roleId':None, 'category':None, 'minSevenDayEpc':None,
             'minNinetyDayEpc':None, 'minPayoutRank':None}

gflags.DEFINE_enum(
    'relationshipStatus', None,
    ['APPROVED', 'AVAILABLE', 'PENDING', 'DECLINED', 'DEACTIVATED'],
    'Status of the relationship')

gflags.DEFINE_string(
    'advertiserId', None,
    'Advertiser ID to lookup (get requests only).')

gflags.DEFINE_string('category', None,
                     'Caret delimited set of advertiser categories to include'
                     + ' (list requests only).')

gflags.DEFINE_string('minSevenDayEpc', None,
                     'Minimum value for the advertiser\'s seven day EPC'
                     + ' (list requests only).')

gflags.DEFINE_string('minNinetyDayEpc', None,
                     'Minimum value for the advertiser\'s ninety day EPC'
                     + ' (list requests only).')

gflags.DEFINE_enum('minPayoutRank', None, ['1', '2', '3', '4'],
                   'Minimum value for the advertiser\'s payout rank'
                   + ' (list requests only)')

def usage(argv):
  print 'Usage: %s <role> <role-id>\n%s' % (argv[0], FLAGS)
  sys.exit(1)


def main(argv):
  # Let the gflags module process the command-line arguments
  try:
    argv = FLAGS(argv)
  except gflags.FlagsError, e:
    print e
    usage(argv)

  if len(argv) != 3:
    usage(argv)
  params = {
    'role': argv[1],
    'roleId': argv[2]
  }

  # Set the logging according to the command-line flag
  logging.getLogger().setLevel(getattr(logging, FLAGS.logging_level))

  # If the Credentials don't exist or are invalid run through the native client
  # flow. The Storage object will ensure that if successful the good
  # Credentials will get written back to a file.
  storage = Storage(FLAGS.credentials_filename)
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    credentials = run(FLOW, storage)

  # Create an httplib2.Http object to handle our HTTP requests and authorize it
  # with our good Credentials.
  http = httplib2.Http()
  http = credentials.authorize(http)

  service = build('gan', 'v1beta1', http=http)

  advertisers = service.advertisers()

  # Filter out all params that aren't set.
  for key in FLAGS:
    if key in API_FLAGS and FLAGS[key].value != None:
      params[key] = FLAGS[key].value

  # Retrieve the relevant advertisers.
  stdout = {}
  html = {}
  try:
    if FLAGS.request_type == "GET":
      get_call = advertisers.get(**params)

      stdout = get_call.execute()
      html['items'] = [stdout['item']]
    else:
      all_items = []
      request = advertisers.list(**params)
      while request:
        response = request.execute()
        if 'items' in response:
          all_items.extend(response['items'])
        request = advertisers.list_next(request, response)

      html['items'] = all_items
      stdout = html
  except apiclient.errors.HttpError, e:
    print json.dumps(e.__dict__, sort_keys=True, indent=4)

  if FLAGS.output_type in ["BOTH", "HTML"]:
    template = get_template('advertisers_template.html')
    context = Context(html)

    out = open("output.html", 'w')
    out.write(template.render(context).encode('UTF-8'))
    os.fchmod(out.fileno(), stat.S_IROTH|stat.S_IRGRP|stat.S_IRUSR|stat.S_IWUSR)
    out.close()

    print 'Wrote output.html'

  if FLAGS.output_type in ["BOTH", "STDOUT"]:
    print json.dumps(stdout, sort_keys=True, indent=4)

if __name__ == '__main__':
  main(sys.argv)
