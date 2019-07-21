#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Google Inc. All Rights Reserved.

"""Queries with paginated results against the shopping search API"""

import pprint

from googleapiclient.discovery import build

try:
  input = raw_input
except NameError:
  pass


SHOPPING_API_VERSION = 'v1'
DEVELOPER_KEY = 'AIzaSyACZJW4JwcWwz5taR2gjIMNQrtgDLfILPc'


def main():
  """Get and print a the entire paginated feed of public products in the United
  States.

  Pagination is controlled with the "startIndex" parameter passed to the list
  method of the resource.
  """
  client = build('shopping', SHOPPING_API_VERSION, developerKey=DEVELOPER_KEY)
  resource = client.products()
  # The first request contains the information we need for the total items, and
  # page size, as well as returning the first page of results.
  request = resource.list(source='public', country='US', q=u'digital camera')
  response = request.execute()
  itemsPerPage = response['itemsPerPage']
  totalItems = response['totalItems']
  for i in range(1, totalItems, itemsPerPage):
    answer = input('About to display results from %s to %s, y/(n)? ' %
                   (i, i + itemsPerPage))
    if answer.strip().lower().startswith('n'):
      # Stop if the user has had enough
      break
    else:
      # Fetch this series of results
      request = resource.list(source='public', country='US',
                              q=u'digital camera', startIndex=i)
      response = request.execute()
      pprint.pprint(response)


if __name__ == '__main__':
    main()
