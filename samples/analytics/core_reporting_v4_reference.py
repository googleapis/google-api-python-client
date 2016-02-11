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

This application demonstrates how to use the Python client library to access
all the pieces of data returned by the Google Analytics Core Reporting API v4.

The application manages authorization by saving an OAuth2.0 token in a local
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
  Google Analytics web interface.

Sample Usage:

  $ python core_reporting_v4_reference.py ga:xxxx

Where the table ID is used to identify from which Google Analytics profile
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


def main(argv):
  # Authenticate and construct service.
  service, flags = sample_tools.init(
      argv, 'analytics', 'v4', __doc__, __file__, parents=[argparser],
      scope='https://www.googleapis.com/auth/analytics.readonly',
      discovery_service_url='https://analytics.googleapis.com/$discovery/google_rest/rest?key=AIzaSyDMNb369FUbBHlZBwFMI83ukWVUzr_D6J8&labels=TRUSTED_TESTER')

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

  apply_orderby(report_request)

  apply_date_ranges(report_request)

  apply_metrics(report_request)

  apply_dimensions(report_request)

  apply_dimension_filter(report_request)

  apply_metric_filter(report_request)

  apply_segment(report_request)

  apply_pivot(report_request)

  # Note that multiple requests can potentially be sent in a single batch
  body = {
      'reportRequests': [report_request]
  }
  return service.reports().batchGet(body=body)


def apply_segment(report_request, not_from_newyork_segment):
  # Creating a segment for users who are NOT from New York by applying a dimension
  # filter on ga:city and inverting the match using 'matchComplement'
  # property.
  not_from_newyork_segment = {
      'name': 'Users NOT from New York', 'sessionSegment':
          {
              'segmentFilters':
                  [
                      {'simpleSegment':
       {
           'orFiltersForSegment':
               [
                   {
                       'segmentFilterClauses':
                           [
                               {
                                   'dimensionFilter':
                                       {
                                           'dimensionName': 'ga:city',
                                           'expressions':
                                               [
                                                   'New York'
                                               ]
                                       }
                               }
                           ]
                   }
               ]
       },
                       'matchComplement':True}
                  ]
          }
  }
  segment = {'dynamicSegment': not_from_newyork_segment}
  report_request['segments'] = [segment]


def apply_pivot(report_request):
  pivot = {
      'metrics': [
          {
              'expression': 'ga:sessions'
          }
      ],
      'dimensions': [
          {
              'name': 'ga:browser'
          },
          {
              'name': 'ga:city'
          }
      ],
      'dimensionFilterClauses': [
          {
              'filters':
                  [
                      {
                          'dimensionName': 'ga:browser',
                          'operator': 'IN_LIST',
                          'expressions': ['Chrome', 'Safari', 'Firefox', 'IE']
                      }
                  ]
          }
      ]
  }
  report_request['pivots'] = [pivot]


def apply_metrics(report_request, original_date_range):
  # Metrics definition
  metrics = [
      {
          'expression': 'ga:sessions'
      },
      {
          'expression': 'ga:sessionDuration'
      }
  ]
  report_request['metrics'] = metrics


def apply_date_ranges(report_request):
  # If two date ranges are specified, the second range will be used to compare
  # data against the first range.
  original_date_range = {
      'startDate': '2015-05-01',
      'endDate': '2016-02-01'
  }
  comparison_date_range = {
      'startDate': '2014-05-01',
      'endDate': '2015-06-01'
  }
  report_request['dateRanges'] = [original_date_range, comparison_date_range]


def apply_dimension_filter(report_request):
  # Include only data from organic search results
  dimension_filter = {
      'dimensionName': 'ga:medium',
      'expressions': ['organic'],
      'operator': 'EXACT'
  }
  dimension_filter_clauses = {
      'filters': [dimension_filter]}
  report_request['dimensionFilterClauses'] = [dimension_filter_clauses]


def apply_dimensions(report_request):
  #  Dimensions definition
  dimensions = [
      {
          'name': 'ga:source'
      },
      {
          'name': 'ga:keyword'
      },
      {
          'name': 'ga:sessionCount',
          # This dimension definition groups the values of ga:sessionCount into four distinct
          # buckets: <10, [10-100), [100, 200), >= 200 sec
          'histogramBuckets': [10, 100, 200]
      },
      {
          # ga:segment is a special dimension that holds the information about the row's segment.
          # Remove it if you are not using segments in the query.
          'name': 'ga:segment'
      }
  ]
  report_request['dimensions'] = dimensions


def apply_orderby(report_request):
  # Order report by sessions count, descending.
  order_by = {'fieldName': 'ga:sessions desc',
              'orderType': 'VALUE'}
  report_request['orderBys'] = [order_by]


def apply_metric_filter(report_request):
  # Note that metric filters will only apply to the 'original' (first) date
  # range.
  sessions_metric_filter = {
      'metricName': 'ga:sessions',
      'comparisonValue': '5',
      'operator': 'GREATER_THAN'
  }
  session_duration_metric_filter = {
      'metricName': 'ga:sessionDuration',
      'comparisonValue': '2500',
      'operator': 'GREATER_THAN'
  }

  # Combine multiple metric filters using AND operator
  metric_filter_clause = {
      'filters':
          [
              sessions_metric_filter,
              session_duration_metric_filter
          ],
      'operator': 'AND'
  }
  report_request['metricFilterClauses'] = [metric_filter_clause]


def print_results(results):
  """Prints all the results in the Core Reporting API Response.

  Args:
    results: The response returned from the Core Reporting API.
  """
  # print_response_info(results)
  reports = results.get('reports')
  if len(reports) == 0:
    print('No reports included in response')
    return

  print('Query cost = %s' % results.get('queryCost', 'n/a'))

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
    print('\tDimension name =  %s' % dimension)
  print()

  metricHeader = headers.get('metricHeader')
  for metric in metricHeader.get('metricHeaderEntries'):
    # Print metric name.
    print('\tMetric name = %s' % metric.get('name'))
    print('\tMetric type = %s' % metric.get('type'))
    print()


def print_totals_for_all_results(report):
  """Prints the total metric value for all pages the query matched.

  Args:
    results: The response returned from the Core Reporting API.
  """

  data = report.get('data')
  print('Total Metrics For All Results:')

  print('\tisDataGolden = %s' % data.get('isDataGolden'))
  print('\tThis query returned %s rows.' % len(data.get('rows', [])))
  print(('\tBut the query matched %s total results.' %
         data.get('rowCount')))
  print()

  print('Here are the metric TOTALS for the matched total results.')
  print_date_ranges(data.get('totals'), report.get('columnHeader'))
  print()

  print('Here are the metric MINIMUMS for the matched total results.')
  print_date_ranges(data.get('minimums'), report.get('columnHeader'))
  print()

  print('Here are the metric MAXIMUMS for the matched total results.')
  print_date_ranges(data.get('maximums'), report.get('columnHeader'))
  print()


def print_metrics(date_range, column_header):
  for metric_index, metric_value in enumerate(date_range.get('values', [])):
    metric_name = column_header.get('metricHeader', {}).get(
        'metricHeaderEntries', [])[metric_index].get('name')

    print('\tMetric  = %s' % metric_name)
    print('\tValue = %s' % metric_value)
    print()

def print_pivot_dimensions(pivot_header_entry):
    for dimension_index, dimension_name in enumerate( pivot_header_entry.get('dimensionNames', [])):
      print('\t\t\tPivot dimension name = %s' % dimension_name)

      dimension_value = pivot_header_entry.get('dimensionValues')[dimension_index]
      print('\t\t\tPivot dimension value = %s' % dimension_value)
      
def print_pivot_values(date_range, column_header):
  pivot_values = date_range.get('pivotValues')
  if pivot_values:
    # Iterate through every pivot region
    for pivot_region_index, pivot_region in enumerate(pivot_values):
      print('"\t\tPivot region #%d' % pivot_region_index)

      if pivot_region.get('values'):
        # Iterate through every metric column within the current pivot region
        for pivot_metric_index, pivot_value in enumerate(
            pivot_region.get('values')):

          # Obtain the pivot header entry object from the report header that will be used to
          # display the pivot header for the current column
          pivot_header_entry = (
              column_header.get('metricHeader').get('pivotHeaders')
              [pivot_region_index].get('pivotHeaderEntries')
              [pivot_metric_index])

          # Print the dimension section of the pivot header
          print_pivot_dimensions(pivot_header_entry)

          # Print the pivot metric name
          pivot_name = pivot_header_entry.get('metric', {}).get('name')
          print('"\t\t\tPivot metric name = %s' % pivot_name)

          # Print the pivot metric value
          print('\t\t\tPivot metric value = ' + pivot_value)

          print()
      print()


def print_date_ranges(date_ranges, column_header):
  """Prints the contents of each date range object: metric values and pivots
  """
  for date_range_index, date_range in enumerate(date_ranges):
    print('\tDate range #%d' % date_range_index)

    print_metrics(date_range, column_header)
    print_pivot_values(date_range, column_header)


def print_dimensions(dimension_values, column_header):
  """Prints dimensions
  """
  for dimension_index, value in enumerate(dimension_values):
    dimension_name = column_header.get('dimensions')[dimension_index]
    print('\tDimension name = %s' % dimension_name)
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
    for index, row in enumerate(data.get('rows')):
      print('Row %d' % index)
      print_dimensions(row.get('dimensions'))
      print_date_ranges(row.get('metrics'), report.get('columnHeader'))
      print()
  else:
    print('No Rows Found')


if __name__ == '__main__':
  main(sys.argv)
