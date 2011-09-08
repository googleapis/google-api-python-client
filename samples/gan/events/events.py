#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Google Inc.

"""Sample for retrieving credit-card offers from GAN."""

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
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run

settings.configure(DEBUG=True, TEMPLATE_DEBUG=True,
    TEMPLATE_DIRS=('.'))


FLAGS = gflags.FLAGS

# Set up a Flow object to be used if we need to authenticate. This
# sample uses OAuth 2.0, and we set up the OAuth2WebServerFlow with
# the information it needs to authenticate. Note that it is called
# the Web Server Flow, but it can also handle the flow for native
# applications <http://code.google.com/apis/accounts/docs/OAuth2.html#IA>
# The client_id client_secret are copied from the API Access tab on
# the Google APIs Console <http://code.google.com/apis/console>. When
# creating credentials for this application be sure to choose an Application
# type of "Installed application".
FLOW = OAuth2WebServerFlow(
    client_id='767567128246-ti2q06i1neqm5boe2m1pqdc2riivhk41.apps.googleusercontent.com',
    client_secret='UtdXI8nKD2SEcQRLQDZPkGT9',
    scope='https://www.googleapis.com/auth/gan.readonly',
    user_agent='gan-events-sample/1.0')

# The gflags module makes defining command-line options easy for
# applications. Run this program with the '--help' argument to see
# all the flags that it understands.
gflags.DEFINE_enum('logging_level', 'DEBUG',
    ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    'Set the level of logging detail.')

gflags.DEFINE_enum("output_type", 'STDOUT', ['BOTH', 'HTML', 'STDOUT'],
                   'Set how to output the results received from the API')

gflags.DEFINE_string('credentials_filename', 'events.dat',
                     'File to store credentials in', short_name='cf')

API_FLAGS = {'eventDateMin':None, 'eventDateMax':None, 'advertiserId':None,
             'publisherId':None, 'orderId':None, 'sku':None,
             'productCategory':None, 'linkId':None, 'memberId':None,
             'status':None, 'type':None, 'role':None, 'roleId':None}

gflags.DEFINE_string(
    'eventDateMin', None,
    'RFC 3339 formatted min date. Ex: 2005-08-09-T10:57:00-08:00')

gflags.DEFINE_string(
    'eventDateMax', None,
    'RFC 3339 formatted max date. Ex: 2005-08-09-T10:57:00-08:00')

gflags.DEFINE_string('advertiserId', None,
                     'caret delimited advertiser IDs')

gflags.DEFINE_string('publisherId', None,
                     'caret delimited publisher IDs')

gflags.DEFINE_string('orderId', None,
                     'caret delimited order IDs')

gflags.DEFINE_string('sku', None,
                     'caret delimited SKUs')

gflags.DEFINE_string('productCategory', None,
                     'caret delimited product categories')

gflags.DEFINE_string('linkId', None,
                     'caret delimited link IDs')

gflags.DEFINE_string('memberId', None,
                     'caret delimited member IDs')

gflags.DEFINE_string('status', None,
                     'status of events - valid values "active" or "cancelled"')

gflags.DEFINE_string('type', None,
                     'type of events - valid values "action" or "transaction"')


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

  events = service.events()

  # Filter out all params that aren't set.
  for key in FLAGS:
    if key in API_FLAGS and FLAGS[key].value != None:
      params[key] = FLAGS[key].value

  # Retrieve the relevant events.
  try:
    list_call = events.list(**params)
    list = list_call.execute()
  except apiclient.errors.HttpError, e:
    print json.dumps(e.__dict__, sort_keys=True, indent=4)

  if FLAGS.output_type in ["BOTH", "HTML"]:
    template = get_template('events_template.html')
    context = Context(list)

    out = open("output.html", 'w')
    out.write(template.render(context).encode('UTF-8'))
    os.fchmod(out.fileno(), stat.S_IROTH|stat.S_IRGRP|stat.S_IRUSR|stat.S_IWUSR)
    out.close()

    print 'Wrote output.html'

  if FLAGS.output_type in ["BOTH", "STDOUT"]:
    print json.dumps(list, sort_keys=True, indent=4)

if __name__ == '__main__':
  main(sys.argv)
