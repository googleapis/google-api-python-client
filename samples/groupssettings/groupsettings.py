#!/usr/bin/python
#
# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Sample for the Group Settings API demonstrates get and update method.

Usage:
  $ python groupsettings.py

You can also get help on all the command-line flags the program understands
by running:

  $ python groupsettings.py --help
"""
from __future__ import print_function

__author__ = 'Shraddha Gupta <shraddhag@google.com>'

from optparse import OptionParser
import os

import pprint
import sys
from googleapiclient.discovery import build
import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow


# CLIENT_SECRETS, name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret, which are found
# on the API Access tab on the Google APIs
# Console <http://code.google.com/apis/console>
CLIENT_SECRETS = 'client_secrets.json'

# Helpful message to display in the browser if the CLIENT_SECRETS file
# is missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the APIs Console <https://code.google.com/apis/console>.

""" % os.path.join(os.path.dirname(__file__), CLIENT_SECRETS)


def access_settings(service, groupId, settings):
  """Retrieves a group's settings and updates the access permissions to it.

  Args:
    service: object service for the Group Settings API.
    groupId: string identifier of the group@domain.
    settings: dictionary key-value pairs of properties of group.
  """

  # Get the resource 'group' from the set of resources of the API.
  # The Group Settings API has only one resource 'group'.
  group = service.groups()

  # Retrieve the group properties
  g = group.get(groupUniqueId=groupId).execute()
  print('\nGroup properties for group %s\n' % g['name'])
  pprint.pprint(g)

  # If dictionary is empty, return without updating the properties.
  if not settings.keys():
    print('\nGive access parameters to update group access permissions\n')
    return

  body = {}

  # Settings might contain null value for some keys(properties). 
  # Extract the properties with values and add to dictionary body.
  for key in settings.iterkeys():
    if settings[key] is not None:
      body[key] = settings[key]

  # Update the properties of group
  g1 = group.update(groupUniqueId=groupId, body=body).execute()

  print('\nUpdated Access Permissions to the group\n')
  pprint.pprint(g1)


def main(argv):
  """Demos the setting of the access properties by the Groups Settings API."""
  usage = 'usage: %prog [options]'
  parser = OptionParser(usage=usage)
  parser.add_option('--groupId',
                    help='Group email address')
  parser.add_option('--whoCanInvite',
                    help='Possible values: ALL_MANAGERS_CAN_INVITE, '
                    'ALL_MEMBERS_CAN_INVITE')
  parser.add_option('--whoCanJoin',
                    help='Possible values: ALL_IN_DOMAIN_CAN_JOIN, '
                    'ANYONE_CAN_JOIN, CAN_REQUEST_TO_JOIN, '
                    'CAN_REQUEST_TO_JOIN')
  parser.add_option('--whoCanPostMessage',
                    help='Possible values: ALL_IN_DOMAIN_CAN_POST, '
                    'ALL_MANAGERS_CAN_POST, ALL_MEMBERS_CAN_POST, '
                    'ANYONE_CAN_POST, NONE_CAN_POST')
  parser.add_option('--whoCanViewGroup',
                    help='Possible values: ALL_IN_DOMAIN_CAN_VIEW, '
                    'ALL_MANAGERS_CAN_VIEW, ALL_MEMBERS_CAN_VIEW, '
                    'ANYONE_CAN_VIEW')
  parser.add_option('--whoCanViewMembership',
                    help='Possible values: ALL_IN_DOMAIN_CAN_VIEW, '
                    'ALL_MANAGERS_CAN_VIEW, ALL_MEMBERS_CAN_VIEW, '
                    'ANYONE_CAN_VIEW')
  (options, args) = parser.parse_args()

  if options.groupId is None:
    print('Give the groupId for the group')
    parser.print_help()
    return

  settings = {}

  if (options.whoCanInvite or options.whoCanJoin or options.whoCanPostMessage
      or options.whoCanPostMessage or options.whoCanViewMembership) is None:
    print('No access parameters given in input to update access permissions')
    parser.print_help()
  else:
    settings = {'whoCanInvite': options.whoCanInvite,
                'whoCanJoin': options.whoCanJoin,
                'whoCanPostMessage': options.whoCanPostMessage,
                'whoCanViewGroup': options.whoCanViewGroup,
                'whoCanViewMembership': options.whoCanViewMembership}

  # Set up a Flow object to be used if we need to authenticate.
  FLOW = flow_from_clientsecrets(CLIENT_SECRETS,
      scope='https://www.googleapis.com/auth/apps.groups.settings',
      message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage('groupsettings.dat')
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    print('invalid credentials')
    # Save the credentials in storage to be used in subsequent runs.
    credentials = run_flow(FLOW, storage)

  # Create an httplib2.Http object to handle our HTTP requests and authorize it
  # with our good Credentials.
  http = httplib2.Http()
  http = credentials.authorize(http)

  service = build('groupssettings', 'v1', http=http)

  access_settings(service=service, groupId=options.groupId, settings=settings)

if __name__ == '__main__':
  main(sys.argv)
