#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2011 Google Inc. All Rights Reserved.
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

"""Reference command-line example for Google Analytics Management API v3.

This application demonstrates how to use the python client library to access
all the pieces of data returned by the Google Analytics Management API v3.

The application manages autorization by saving an OAuth2.0 token in a local
file and reusing the token for subsequent requests. It then traverses the
Google Analytics Management hiearchy. It first retrieves and prints all the
authorized user's accounts, next it prints all the web properties for the
first account, then all the profiles for the first web property and finally
all the goals for the first profile. The sample then prints all the
user's advanced segments.

To read an indepth discussion on how this file works, check out the Management
API Python Getting Started guide here:
http://code.google.com/apis/analytics/docs/mgmt/v3/mgmtPython.html

Usage:

Before you begin, you should register your application as an installed
application to get your own Project / OAUth2 Client ID / Secret:
https://code.google.com/apis/console

Learn more about registering your Analytics Application here:
http://code.google.com/apis/analytics/docs/mgmt/v3/mgmtPython.html#authorize

  $ python analytics.py

Also you can also get help on all the command-line flags the program
understands by running:

  $ python analytics.py --help
"""

__author__ = 'api.nickm@ (Nick Mihailovski)'

import sys

from apiclient.discovery import build
from apiclient.errors import HttpError

import gflags
import httplib2

from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage
from oauth2client.tools import run

FLAGS = gflags.FLAGS


# Remember to get your own client_id / client_secret in the
# Google API developer console: https://code.google.com/apis/console
FLOW = OAuth2WebServerFlow(
    client_id='INSERT_YOUR_CLIENT_ID_HERE',
    client_secret='INSERT_YOUR_CLIENT_SECRET_HERE',
    scope='https://www.googleapis.com/auth/analytics.readonly',
    user_agent='analytics-api-v3-awesomeness')

TOKEN_FILE_NAME = 'analytics.dat'


def main(argv):
  # Let the gflags module process the command-line arguments
  try:
    argv = FLAGS(argv)
  except gflags.FlagsError, e:
    print '%s\\nUsage: %s ARGS\\n%s' % (e, argv[0], FLAGS)
    sys.exit(1)

  # Manage re-using tokens.
  storage = Storage(TOKEN_FILE_NAME)
  credentials = storage.get()
  if not credentials or credentials.invalid:
    # Get a new token.
    credentials = run(FLOW, storage)

  # Build an authorized service object.
  http = httplib2.Http()
  http = credentials.authorize(http)
  service = build('analytics', 'v3', http=http)

  # Traverse the Management hiearchy and print results.
  try:
    traverse_hiearchy(service)

  except HttpError, error:
    print ('Arg, there was an API error : %s %s : %s' %
            (error.resp.status, error.resp.reason, error._get_reason()))

  except AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run'
           'the application to re-authorize')


def traverse_hiearchy(service):
  """Traverses the management API hiearchy and prints results.

  This retrieves and prints the authorized user's accounts. It then
  retrieves and prints all the web properties for the first account,
  retrieves and prints all the profiles for the first web property,
  and retrieves and prints all the goals for the first profile.

  Args:
    service: The service object built by the Google API Python client library.

  Raises:
    HttpError: If an error occured when accessing the API.
    AccessTokenRefreshError: If the current token was invalid.
  """
  view = View()

  accounts = service.management().accounts().list().execute()

  view.print_accounts(accounts)

  if accounts.get('items'):
    firstAccountId = accounts.get('items')[0].get('id')
    webproperties = service.management().webproperties().list(
        accountId=firstAccountId).execute()

    view.print_webproperties(webproperties)

    if webproperties.get('items'):
      firstWebpropertyId = webproperties.get('items')[0].get('id')
      profiles = service.management().profiles().list(
          accountId=firstAccountId,
          webPropertyId=firstWebpropertyId).execute()

      view.print_profiles(profiles)

      if profiles.get('items'):
        firstProfileId = profiles.get('items')[0].get('id')
        goals = service.management().goals().list(
            accountId=firstAccountId,
            webPropertyId=firstWebpropertyId,
            profileId=firstProfileId).execute()

        view.print_goals(goals)

  view.print_segments(service.management().segments().list().execute())


class View(object):
  """Utility class to print various Management API collections."""

  def print_accounts(self, accounts_list):
    """Prints all the account info in the Accounts Collection."""

    print '------ Account Collection -------'
    self.print_pagination_info(accounts_list)
    print

    for account in accounts_list.get('items'):
      print 'Account ID      = %s' % account.get('id')
      print 'Kind            = %s' % account.get('kind')
      print 'Self Link       = %s' % account.get('selfLink')
      print 'Account Name    = %s' % account.get('name')
      print 'Created         = %s' % account.get('created')
      print 'Updated         = %s' % account.get('updated')

      child_link = account.get('childLink')
      print 'Child link href = %s' % child_link.get('href')
      print 'Child link type = %s' % child_link.get('type')
      print

  def print_webproperties(self, webproperties_list):
    """Prints all the web property info in the WebProperties Collection."""

    print '------ Web Properties Collection -------'
    self.print_pagination_info(webproperties_list)
    print

    for webproperty in webproperties_list.get('items'):
      print 'Kind               = %s' % webproperty.get('kind')
      print 'Account ID         = %s' % webproperty.get('accountId')
      print 'Web Property ID    = %s' % webproperty.get('id')
      print ('Internal Web Property ID = %s' %
             webproperty.get('internalWebPropertyId'))

      print 'Website URL        = %s' % webproperty.get('websiteUrl')
      print 'Created            = %s' % webproperty.get('created')
      print 'Updated            = %s' % webproperty.get('updated')

      print 'Self Link          = %s' % webproperty.get('selfLink')
      parent_link = webproperty.get('parentLink')
      print 'Parent link href   = %s' % parent_link.get('href')
      print 'Parent link type   = %s' % parent_link.get('type')
      child_link = webproperty.get('childLink')
      print 'Child link href    = %s' % child_link.get('href')
      print 'Child link type    = %s' % child_link.get('type')
      print

  def print_profiles(self, profiles_list):
    """Prints all the profile info in the Profiles Collection."""

    print '------ Profiles Collection -------'
    self.print_pagination_info(profiles_list)
    print

    for profile in profiles_list.get('items'):
      print 'Kind                      = %s' % profile.get('kind')
      print 'Account ID                = %s' % profile.get('accountId')
      print 'Web Property ID           = %s' % profile.get('webPropertyId')
      print ('Internal Web Property ID = %s' %
             profile.get('internalWebPropertyId'))
      print 'Profile ID                = %s' % profile.get('id')
      print 'Profile Name              = %s' % profile.get('name')

      print 'Currency         = %s' % profile.get('currency')
      print 'Timezone         = %s' % profile.get('timezone')
      print 'Default Page     = %s' % profile.get('defaultPage')

      print ('Exclude Query Parameters        = %s' %
             profile.get('excludeQueryParameters'))
      print ('Site Search Category Parameters = %s' %
             profile.get('siteSearchCategoryParameters'))
      print ('Site Search Query Parameters    = %s' %
             profile.get('siteSearchQueryParameters'))

      print 'Created          = %s' % profile.get('created')
      print 'Updated          = %s' % profile.get('updated')

      print 'Self Link        = %s' % profile.get('selfLink')
      parent_link = profile.get('parentLink')
      print 'Parent link href = %s' % parent_link.get('href')
      print 'Parent link type = %s' % parent_link.get('type')
      child_link = profile.get('childLink')
      print 'Child link href  = %s' % child_link.get('href')
      print 'Child link type  = %s' % child_link.get('type')
      print

  def print_goals(self, goals_list):
    """Prints all the goal info in the Goals Collection."""

    print '------ Goals Collection -------'
    self.print_pagination_info(goals_list)
    print

    for goal in goals_list.get('items'):
      print 'Goal ID     = %s' % goal.get('id')
      print 'Kind        = %s' % goal.get('kind')
      print 'Self Link        = %s' % goal.get('selfLink')

      print 'Account ID               = %s' % goal.get('accountId')
      print 'Web Property ID          = %s' % goal.get('webPropertyId')
      print ('Internal Web Property ID = %s' %
             goal.get('internalWebPropertyId'))
      print 'Profile ID               = %s' % goal.get('profileId')

      print 'Goal Name   = %s' % goal.get('name')
      print 'Goal Value  = %s' % goal.get('value')
      print 'Goal Active = %s' % goal.get('active')
      print 'Goal Type   = %s' % goal.get('type')

      print 'Created     = %s' % goal.get('created')
      print 'Updated     = %s' % goal.get('updated')

      parent_link = goal.get('parentLink')
      print 'Parent link href = %s' % parent_link.get('href')
      print 'Parent link type = %s' % parent_link.get('type')

      # Print the goal details depending on the type of goal.
      if goal.get('urlDestinationDetails'):
        self.print_url_destination_goal_details(
            goal.get('urlDestinationDetails'))

      elif goal.get('visitTimeOnSiteDetails'):
        self.print_visit_time_on_site_goal_details(
            goal.get('visitTimeOnSiteDetails'))

      elif goal.get('visitNumPagesDetails'):
        self.print_visit_num_pages_goal_details(
            goal.get('visitNumPagesDetails'))

      elif goal.get('eventDetails'):
        self.print_event_goal_details(goal.get('eventDetails'))

      print

  def print_url_destination_goal_details(self, goal_details):
    """Prints all the URL Destination goal type info."""

    print '------ Url Destination Goal -------'
    print 'Goal URL            = %s' % goal_details.get('url')
    print 'Case Sensitive      = %s' % goal_details.get('caseSensitive')
    print 'Match Type          = %s' % goal_details.get('matchType')
    print 'First Step Required = %s' % goal_details.get('firstStepRequired')

    print '------ Url Destination Goal Steps -------'
    if goal_details.get('steps'):
      for goal_step in goal_details.get('steps'):
        print 'Step Number  = %s' % goal_step.get('number')
        print 'Step Name    = %s' % goal_step.get('name')
        print 'Step URL     = %s' % goal_step.get('url')
    else:
      print 'No Steps Configured'

  def print_visit_time_on_site_goal_details(self, goal_details):
    """Prints all the Visit Time On Site goal type info."""

    print '------ Visit Time On Site Goal -------'
    print 'Comparison Type  = %s' % goal_details.get('comparisonType')
    print 'comparison Value = %s' % goal_details.get('comparisonValue')

  def print_visit_num_pages_goal_details(self, goal_details):
    """Prints all the Visit Num Pages goal type info."""

    print '------ Visit Num Pages Goal -------'
    print 'Comparison Type  = %s' % goal_details.get('comparisonType')
    print 'comparison Value = %s' % goal_details.get('comparisonValue')

  def print_event_goal_details(self, goal_details):
    """Prints all the Event goal type info."""

    print '------ Event Goal -------'
    print 'Use Event Value  = %s' % goal_details.get('useEventValue')

    for event_condition in goal_details.get('eventConditions'):
      event_type = event_condition.get('type')
      print 'Type             = %s' % event_type

      if event_type in ('CATEGORY', 'ACTION', 'LABEL'):
        print 'Match Type       = %s' % event_condition.get('matchType')
        print 'Expression       = %s' % event_condition.get('expression')
      else:  # VALUE type.
        print 'Comparison Type  = %s' % event_condition.get('comparisonType')
        print 'Comparison Value = %s' % event_condition.get('comparisonValue')

  def print_segments(self, segments_list):
    """Prints all the segment info in the Segments Collection."""

    print '------ Segments Collection -------'
    self.print_pagination_info(segments_list)
    print

    for segment in segments_list.get('items'):
      print 'Segment ID = %s' % segment.get('id')
      print 'Kind       = %s' % segment.get('kind')
      print 'Self Link  = %s' % segment.get('selfLink')
      print 'Name       = %s' % segment.get('name')
      print 'Definition = %s' % segment.get('definition')
      print 'Created    = %s' % segment.get('created')
      print 'Updated    = %s' % segment.get('updated')
      print

  def print_pagination_info(self, mgmt_list):
    """Prints common pagination details."""

    print 'Items per page = %s' % mgmt_list.get('itemsPerPage')
    print 'Total Results  = %s' % mgmt_list.get('totalResults')
    print 'Start Index    = %s' % mgmt_list.get('startIndex')

    # These only have values if other result pages exist.
    if mgmt_list.get('previousLink'):
      print 'Previous Link  = %s' % mgmt_list.get('previousLink')
    if mgmt_list.get('nextLink'):
      print 'Next Link      = %s' % mgmt_list.get('nextLink')


if __name__ == '__main__':
  main(sys.argv)

