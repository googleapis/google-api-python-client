#!/usr/bin/python
# -*- coding: utf-8 -*-
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


Before You Begin:

Update the client_secrets.json file

  You must update the clients_secrets.json file with a client id, client
  secret, and the redirect uri. You get these values by creating a new project
  in the Google APIs console and registering for OAuth2.0 for installed
  applications: https://code.google.com/apis/console

  Learn more about registering your analytics application here:
  https://developers.google.com/analytics/devguides/config/mgmt/v3/mgmtAuthorization

Sample Usage:

  $ python management_v3_reference.py

Also you can also get help on all the command-line flags the program
understands by running:

  $ python management_v3_reference.py --help
"""
from __future__ import print_function

__author__ = 'api.nickm@gmail.com (Nick Mihailovski)'

import argparse
import sys

from googleapiclient.errors import HttpError
from googleapiclient import sample_tools
from oauth2client.client import AccessTokenRefreshError


def main(argv):
  # Authenticate and construct service.
  service, flags = sample_tools.init(
      argv, 'analytics', 'v3', __doc__, __file__,
      scope='https://www.googleapis.com/auth/analytics.readonly')

  # Traverse the Management hiearchy and print results or handle errors.
  try:
    traverse_hiearchy(service)

  except TypeError as error:
    # Handle errors in constructing a query.
    print(('There was an error in constructing your query : %s' % error))

  except HttpError as error:
    # Handle API errors.
    print(('Arg, there was an API error : %s : %s' %
           (error.resp.status, error._get_reason())))

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

  accounts = service.management().accounts().list().execute()
  print_accounts(accounts)

  if accounts.get('items'):
    firstAccountId = accounts.get('items')[0].get('id')
    webproperties = service.management().webproperties().list(
        accountId=firstAccountId).execute()

    print_webproperties(webproperties)

    if webproperties.get('items'):
      firstWebpropertyId = webproperties.get('items')[0].get('id')
      profiles = service.management().profiles().list(
          accountId=firstAccountId,
          webPropertyId=firstWebpropertyId).execute()

      print_profiles(profiles)

      if profiles.get('items'):
        firstProfileId = profiles.get('items')[0].get('id')
        goals = service.management().goals().list(
            accountId=firstAccountId,
            webPropertyId=firstWebpropertyId,
            profileId=firstProfileId).execute()

        print_goals(goals)

  print_segments(service.management().segments().list().execute())


def print_accounts(accounts_response):
  """Prints all the account info in the Accounts Collection.

  Args:
    accounts_response: The response object returned from querying the Accounts
        collection.
  """

  print('------ Account Collection -------')
  print_pagination_info(accounts_response)
  print()

  for account in accounts_response.get('items', []):
    print('Account ID      = %s' % account.get('id'))
    print('Kind            = %s' % account.get('kind'))
    print('Self Link       = %s' % account.get('selfLink'))
    print('Account Name    = %s' % account.get('name'))
    print('Created         = %s' % account.get('created'))
    print('Updated         = %s' % account.get('updated'))

    child_link = account.get('childLink')
    print('Child link href = %s' % child_link.get('href'))
    print('Child link type = %s' % child_link.get('type'))
    print()

  if not accounts_response.get('items'):
    print('No accounts found.\n')


def print_webproperties(webproperties_response):
  """Prints all the web property info in the WebProperties collection.

  Args:
    webproperties_response: The response object returned from querying the
        Webproperties collection.
  """

  print('------ Web Properties Collection -------')
  print_pagination_info(webproperties_response)
  print()

  for webproperty in webproperties_response.get('items', []):
    print('Kind               = %s' % webproperty.get('kind'))
    print('Account ID         = %s' % webproperty.get('accountId'))
    print('Web Property ID    = %s' % webproperty.get('id'))
    print(('Internal Web Property ID = %s' %
           webproperty.get('internalWebPropertyId')))

    print('Website URL        = %s' % webproperty.get('websiteUrl'))
    print('Created            = %s' % webproperty.get('created'))
    print('Updated            = %s' % webproperty.get('updated'))

    print('Self Link          = %s' % webproperty.get('selfLink'))
    parent_link = webproperty.get('parentLink')
    print('Parent link href   = %s' % parent_link.get('href'))
    print('Parent link type   = %s' % parent_link.get('type'))
    child_link = webproperty.get('childLink')
    print('Child link href    = %s' % child_link.get('href'))
    print('Child link type    = %s' % child_link.get('type'))
    print()

  if not webproperties_response.get('items'):
    print('No webproperties found.\n')


def print_profiles(profiles_response):
  """Prints all the profile info in the Profiles Collection.

  Args:
    profiles_response: The response object returned from querying the
        Profiles collection.
  """

  print('------ Profiles Collection -------')
  print_pagination_info(profiles_response)
  print()

  for profile in profiles_response.get('items', []):
    print('Kind                      = %s' % profile.get('kind'))
    print('Account ID                = %s' % profile.get('accountId'))
    print('Web Property ID           = %s' % profile.get('webPropertyId'))
    print(('Internal Web Property ID = %s' %
           profile.get('internalWebPropertyId')))
    print('Profile ID                = %s' % profile.get('id'))
    print('Profile Name              = %s' % profile.get('name'))

    print('Currency         = %s' % profile.get('currency'))
    print('Timezone         = %s' % profile.get('timezone'))
    print('Default Page     = %s' % profile.get('defaultPage'))

    print(('Exclude Query Parameters        = %s' %
           profile.get('excludeQueryParameters')))
    print(('Site Search Category Parameters = %s' %
           profile.get('siteSearchCategoryParameters')))
    print(('Site Search Query Parameters    = %s' %
           profile.get('siteSearchQueryParameters')))

    print('Created          = %s' % profile.get('created'))
    print('Updated          = %s' % profile.get('updated'))

    print('Self Link        = %s' % profile.get('selfLink'))
    parent_link = profile.get('parentLink')
    print('Parent link href = %s' % parent_link.get('href'))
    print('Parent link type = %s' % parent_link.get('type'))
    child_link = profile.get('childLink')
    print('Child link href  = %s' % child_link.get('href'))
    print('Child link type  = %s' % child_link.get('type'))
    print()

  if not profiles_response.get('items'):
    print('No profiles found.\n')


def print_goals(goals_response):
  """Prints all the goal info in the Goals collection.

  Args:
    goals_response: The response object returned from querying the Goals
        collection
  """

  print('------ Goals Collection -------')
  print_pagination_info(goals_response)
  print()

  for goal in goals_response.get('items', []):
    print('Goal ID     = %s' % goal.get('id'))
    print('Kind        = %s' % goal.get('kind'))
    print('Self Link        = %s' % goal.get('selfLink'))

    print('Account ID               = %s' % goal.get('accountId'))
    print('Web Property ID          = %s' % goal.get('webPropertyId'))
    print(('Internal Web Property ID = %s' %
           goal.get('internalWebPropertyId')))
    print('Profile ID               = %s' % goal.get('profileId'))

    print('Goal Name   = %s' % goal.get('name'))
    print('Goal Value  = %s' % goal.get('value'))
    print('Goal Active = %s' % goal.get('active'))
    print('Goal Type   = %s' % goal.get('type'))

    print('Created     = %s' % goal.get('created'))
    print('Updated     = %s' % goal.get('updated'))

    parent_link = goal.get('parentLink')
    print('Parent link href = %s' % parent_link.get('href'))
    print('Parent link type = %s' % parent_link.get('type'))

    # Print the goal details depending on the type of goal.
    if goal.get('urlDestinationDetails'):
      print_url_destination_goal_details(
          goal.get('urlDestinationDetails'))

    elif goal.get('visitTimeOnSiteDetails'):
      print_visit_time_on_site_goal_details(
          goal.get('visitTimeOnSiteDetails'))

    elif goal.get('visitNumPagesDetails'):
      print_visit_num_pages_goal_details(
          goal.get('visitNumPagesDetails'))

    elif goal.get('eventDetails'):
      print_event_goal_details(goal.get('eventDetails'))

    print()

  if not goals_response.get('items'):
    print('No goals found.\n')


def print_url_destination_goal_details(goal_details):
  """Prints all the URL Destination goal type info.

  Args:
    goal_details: The details portion of the goal response.
  """

  print('------ Url Destination Goal -------')
  print('Goal URL            = %s' % goal_details.get('url'))
  print('Case Sensitive      = %s' % goal_details.get('caseSensitive'))
  print('Match Type          = %s' % goal_details.get('matchType'))
  print('First Step Required = %s' % goal_details.get('firstStepRequired'))

  print('------ Url Destination Goal Steps -------')
  for goal_step in goal_details.get('steps', []):
    print('Step Number  = %s' % goal_step.get('number'))
    print('Step Name    = %s' % goal_step.get('name'))
    print('Step URL     = %s' % goal_step.get('url'))

  if not goal_details.get('steps'):
    print('No Steps Configured')


def print_visit_time_on_site_goal_details(goal_details):
  """Prints all the Visit Time On Site goal type info.

  Args:
    goal_details: The details portion of the goal response.
  """

  print('------ Visit Time On Site Goal -------')
  print('Comparison Type  = %s' % goal_details.get('comparisonType'))
  print('comparison Value = %s' % goal_details.get('comparisonValue'))


def print_visit_num_pages_goal_details(goal_details):
  """Prints all the Visit Num Pages goal type info.

  Args:
    goal_details: The details portion of the goal response.
  """

  print('------ Visit Num Pages Goal -------')
  print('Comparison Type  = %s' % goal_details.get('comparisonType'))
  print('comparison Value = %s' % goal_details.get('comparisonValue'))


def print_event_goal_details(goal_details):
  """Prints all the Event goal type info.

  Args:
    goal_details: The details portion of the goal response.
  """

  print('------ Event Goal -------')
  print('Use Event Value  = %s' % goal_details.get('useEventValue'))

  for event_condition in goal_details.get('eventConditions', []):
    event_type = event_condition.get('type')
    print('Type             = %s' % event_type)

    if event_type in ('CATEGORY', 'ACTION', 'LABEL'):
      print('Match Type       = %s' % event_condition.get('matchType'))
      print('Expression       = %s' % event_condition.get('expression'))
    else:  # VALUE type.
      print('Comparison Type  = %s' % event_condition.get('comparisonType'))
      print('Comparison Value = %s' % event_condition.get('comparisonValue'))


def print_segments(segments_response):
  """Prints all the segment info in the Segments collection.

  Args:
    segments_response: The response object returned from querying the
        Segments collection.
  """

  print('------ Segments Collection -------')
  print_pagination_info(segments_response)
  print()

  for segment in segments_response.get('items', []):
    print('Segment ID = %s' % segment.get('id'))
    print('Kind       = %s' % segment.get('kind'))
    print('Self Link  = %s' % segment.get('selfLink'))
    print('Name       = %s' % segment.get('name'))
    print('Definition = %s' % segment.get('definition'))
    print('Created    = %s' % segment.get('created'))
    print('Updated    = %s' % segment.get('updated'))
    print()


def print_pagination_info(management_response):
  """Prints common pagination details.

  Args:
    management_response: The common reponse object for each collection in the
        Management API.
  """

  print('Items per page = %s' % management_response.get('itemsPerPage'))
  print('Total Results  = %s' % management_response.get('totalResults'))
  print('Start Index    = %s' % management_response.get('startIndex'))

  # These only have values if other result pages exist.
  if management_response.get('previousLink'):
    print('Previous Link  = %s' % management_response.get('previousLink'))
  if management_response.get('nextLink'):
    print('Next Link      = %s' % management_response.get('nextLink'))


if __name__ == '__main__':
  main(sys.argv)

