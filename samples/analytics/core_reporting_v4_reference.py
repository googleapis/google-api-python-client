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

"""Reference command-line example for Google Analytics Core Reporting API v4.

This application demonstrates how to use the python client library to access
all the pieces of data returned by the Google Analytics Core Reporting API v4.

The application manages autorization by saving an OAuth2.0 token in a local
file and reusing the token for subsequent requests.

Before You Begin:

Update the client_secrets.json file

  You must update the clients_secrets.json file with a client id, client
  secret, and the redirect uri. You get these values by creating a new project
  in the Google APIs console and registering for OAuth2.0 for installed
  applications: https://code.google.com/apis/console

  Learn more about registering your analytics application here:
  http://developers.google.com/analytics/devguides/reporting/core/v3/gdataAuthorization

Supply your TABLE_ID

  You will also need to identify from which profile to access data by
  specifying the TABLE_ID constant below. This value is of the form: ga:xxxx
  where xxxx is the profile ID. You can get the profile ID by either querying
  the Management API or by looking it up in the account settings of the
  Google Anlaytics web interface.

Sample Usage:

  $ python core_reporting_v4_reference.py ga:xxxx

Where the table ID is used to identify from which Google Anlaytics profile
to retrieve data. This ID is in the format ga:xxxx where xxxx is the
profile ID.

Also you can also get help on all the command-line flags the program
understands by running:

  $ python core_reporting_v4_reference.py --help
"""
from __future__ import print_function

__author__ = 'ikuleshov@google.com (Ilya Kuleshov)'

import argparse
import sys

from googleapiclient.errors import HttpError
from googleapiclient import sample_tools
from oauth2client.client import AccessTokenRefreshError

# Declare command-line flags.
argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('table_id', type=str,
                     help=('The table ID of the profile you wish to access. '
                           'Format is ga:xxx where xxx is your profile ID.'))

# The list of metric ids will be used both to generate a request and display a
# response in human readable form
metrics =  [ { 'expression': 'ga:sessions' }, 
             { 'expression': 'ga:sessionDuration' } 
           ]

# The list of dimensions is, similarly to metrics, is used to both generate a request
# and properly display the response since the response object only contains dimension
# values but no labels.
dimensions = [ {
                 'name':'ga:source'
               },

               {
                 'name': 'ga:keyword'
               },

               {
                 'name': 'ga:sessionDurationBucket',
                 # For session duration dimension, group values into four buckets:
                 # [0..30 secs), [30..60 secs), [60, 1000), [1000, infinity) 
                 'histogramBuckets': [ 30, 60, 1000 ]
                },
                {
                    'name': 'ga:segment'
                }
              ]

def main(argv):
  # Authenticate and construct service.
  service, flags = sample_tools.init(
      argv, 'analytics', 'v4', __doc__, __file__, parents=[argparser],
      scope='https://www.googleapis.com/auth/analytics.readonly', discovery_service_url="https://analytics.googleapis.com/$discovery/google_rest/rest?key=AIzaSyDMNb369FUbBHlZBwFMI83ukWVUzr_D6J8&labels=TRUSTED_TESTER")


  # Try to make a request to the API. Print the results or handle errors.
  try:
    results = get_api_query(service, flags.table_id).execute()
    print_results(results)

  except TypeError as error:
    # Handle errors in constructing a query.
    print(('There was an error in executing your query : %s' % error))

  except HttpError as error:
    # Handle API errors.
    print(('Arg, there was an API error : %s : %s' %
           (error.resp.status, error._get_reason())))

  except AccessTokenRefreshError:
    # Handle Auth errors.
    print ('The credentials have been revoked or expired, please re-run '
           'the application to re-authorize')


def get_api_query(service, table_id):
  """Returns a query object to retrieve data from the Core Reporting API.

  Args:
    service: The service object built by the Google API Python client library.
    table_id: str The table ID form which to retrieve data.
  """
  report_request = {}
  report_request['viewId'] = table_id

  # Optional limit on the maximum page size.
  report_request['pageSize'] = 25

  # Optional indication of the desired sampling level
  report_request['samplingLevel'] = 'LARGE'

  # Order report by sessions count, descending.
  orderBy = {'fieldName': 'ga:sessions desc', 
             'orderType': 'VALUE'}
  report_request['orderBys'] = [ orderBy ]

  # If two date ranges are specified, the second range will be used to compare
  # data against the first range.
  original_date_range = {
          'startDate': '2015-05-01',
          'endDate': '2016-02-01'
  }

  comparison_date_range = {
          'startDate': '2014-05-01',
          'endDate': '2015-02-01'
  }

  report_request['dateRanges'] = [ original_date_range, comparison_date_range ]

  report_request['metrics'] = metrics

  report_request['dimensions'] = dimensions

  # Include only data from organic search results
  dimensionFilter = {'dimensionName': 'ga:medium',
                  'expressions': ['organic'],
                  'operator': 'EXACT'
                  }

  dimensionFilterClauses = {'filters': [ dimensionFilter ]}
  report_request['dimensionFilterClauses'] = [ dimensionFilterClauses ]

  # Note that metric filters will only apply to the 'original' (first) date range.
  sessionsMetricFilter = {'metricName': 'ga:sessions',
                  'comparisonValue': '5',
                  'operator': 'GREATER_THAN'
                  }

  sessionDurationMetricFilter = {'metricName': 'ga:sessionDuration',
                  'comparisonValue': '0',
                  'operator': 'GREATER_THAN'
                  }

  # Combine multiple metric filters using AND operator
  metricFilterClauses = {'filters': [ sessionsMetricFilter,
                                      sessionDurationMetricFilter ],
                         'operator': 'AND'
                         }
  report_request['metricFilterClauses'] = [] # metricFilterClauses ]


  report_request['segments']  =   [ {'dynamicSegment': {'name': 'Users NOT from New York',
                                                       'sessionSegment': { 'segmentFilters': [ 
                                                            { 'simpleSegment': {  'orFiltersForSegment': [ 
                                                                                                          { 'segmentFilterClauses': [
                                                                                                              { 'dimensionFilter': { 'dimensionName': 'ga:city',
                                                                                                                                     'expressions': [ 'New York' ]
                                                                                                                                   }
                                                                                                              }
                                                                                                            ]
                                                                                                           }
                                                                                                        ]
                                                                                },
                                                             'matchComplement': True
                                                             }
                                                            ]
                                        }
                                                       }
                                    }
                                  ]

  # Note that multiple requests can potentially be sent in a single batch
  body = { 'reportRequests': [ report_request ] }
  return service.reports().batchGet( body=body )

def print_results(results):
  """Prints all the results in the Core Reporting API Response.

  Args:
    results: The response returned from the Core Reporting API.
  """
  print_response_info(results)
  reports =  results.get('reports')
  if len( reports ) == 0:
    print("No reports included in response")
    return

  # This example will receive only one report, but response can contain multiple
  # reports, one per each batched request.
  for report in reports:
    print_report_info(report)
    print_column_headers(report)
    print_totals_for_all_results(report)
    print_rows(report)


def print_response_info(results):
  """Prints common response details.

  Args:
    results: The response returned from the Core Reporting API.
  """
  print(results)

def print_report_info(report):
  """Prints general information about this report.

  Args:
    results: The response returned from the Core Reporting API.
  """
  print('Report Infos:')

  # Next page token is None if there is no next page
  print('Next page token         = %s' % report.get('nextPageToken'))
  print()


def print_column_headers(report):
  """Prints the information for each column.

  The main data from the API is returned as rows of data. The column
  headers describe the names and types of each column in rows.


  Args:
    results: The response returned from the Core Reporting API.
  """

  print('Column Headers:')
  headers = report.get('columnHeader')
  for dimension in headers.get('dimensions'):
    # Print Dimension name.
    print('\tDimension name =  %s' % dimension )
  print()


  metricHeader = headers.get('metricHeader')
  for metric in metricHeader.get('metricHeaderEntries'):
    # Print metric name.
    print('\tMetric name = %s' % metric.get('name') )
    print('\tMetric type = %s' % metric.get('type') )
    print()


def print_totals_for_all_results(report):
  """Prints the total metric value for all pages the query matched.

  Args:
    results: The response returned from the Core Reporting API.
  """

  data = report.get('data')
  print('Total Metrics For All Results:')

  print('\tisDataGolden = %s' % data.get('isDataGolden') )
  print('\tThis query returned %s rows.' % len(data.get('rows', [])))
  print(('\tBut the query matched %s total results.' %
         data.get('rowCount')))
  print()

  print('Here are the metric TOTALS for the matched total results.')
  print_date_ranges(data.get('totals'))
  print()

  print('Here are the metric MINIMUMS for the matched total results.')
  print_date_ranges(data.get('minimums'))
  print()

  print('Here are the metric MAXIMUMS for the matched total results.')
  print_date_ranges(data.get('maximums'))
  print()

def print_date_ranges(dateRanges):
  """Prints the contents of date ranges object
  """
  for dateRangeIndex, dateRange in enumerate( dateRanges ):
    print( '\tDate range #%s' % dateRangeIndex )
    for metricIndex, value in enumerate( dateRange.get( 'values', [] ) ):
      # Display metric expression as metric label
      print('\tMetric  = %s' % metrics[ metricIndex ].get('expression'))
      print('\tValue = %s' % value)
      print()

def print_dimensions(dimensionValues):
  """Prints dimensions
  """
  for dimensionIndex, value in enumerate( dimensionValues ):
    print('\tDimension name = %s' % dimensions[ dimensionIndex ].get('name') )
    print('\tDimension value = %s' % value)
    print()

def print_rows(report):
  """Prints all the rows of data returned by the API.

  Args:
    results: The response returned from the Core Reporting API.
  """
  print('Rows:')
  data = report.get('data')
  if data.get('rows', []):
    for index, row in enumerate( data.get('rows') ):
      print( 'Row %d' % index )
      print_date_ranges( row.get('metrics') )
      print_dimensions( row.get('dimensions') )
      print()
  else:
    print('No Rows Found')


if __name__ == '__main__':
  main(sys.argv)
