#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Google Inc. All Rights Reserved.

"""Query with ranked results against the shopping search API"""

import pprint

from googleapiclient.discovery import build


SHOPPING_API_VERSION = 'v1'
DEVELOPER_KEY = 'AIzaSyACZJW4JwcWwz5taR2gjIMNQrtgDLfILPc'


def main():
  """Get and print a feed of public products in the United States mathing a
  text search query for 'digital camera' ranked by ascending price.

  The list method for the resource should be called with the "rankBy"
  parameter.  5 parameters to rankBy are currently supported by the API. They
  are:

  "relevancy"
  "modificationTime:ascending"
  "modificationTime:descending"
  "price:ascending"
  "price:descending"

  These parameters can be combined

  The default ranking is "relevancy" if the rankBy parameter is omitted.
  """
  client = build('shopping', SHOPPING_API_VERSION, developerKey=DEVELOPER_KEY)
  resource = client.products()
  # The rankBy parameter to the list method causes results to be ranked, in
  # this case by ascending price.
  request = resource.list(source='public', country='US', q=u'digital camera',
                          rankBy='price:ascending')
  response = request.execute()
  pprint.pprint(response)


if __name__ == '__main__':
    main()
