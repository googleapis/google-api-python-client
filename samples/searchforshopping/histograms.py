#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Google Inc. All Rights Reserved.

"""Query with ranked results against the shopping search API"""
from __future__ import print_function

from googleapiclient.discovery import build


SHOPPING_API_VERSION = 'v1'
DEVELOPER_KEY = 'AIzaSyACZJW4JwcWwz5taR2gjIMNQrtgDLfILPc'


def main():
  """Get and print a histogram of the top 15 brand distribution for a search
  query.

  Histograms are created by using the "Facets" functionality of the API. A
  Facet is a view of a certain property of products, containing a number of
  buckets, one for each value of that property. Or concretely, for a parameter
  such as "brand" of a product, the facets would include a facet for brand,
  which would contain a number of buckets, one for each brand returned in the
  result.

  A bucket contains either a value and a count, or a value and a range. In the
  simple case of a value and a count for our example of the "brand" property,
  the value would be the brand name, eg "sony" and the count would be the
  number of results in the search.
  """
  client = build('shopping', SHOPPING_API_VERSION, developerKey=DEVELOPER_KEY)
  resource = client.products()
  request = resource.list(source='public', country='US', q=u'digital camera',
                          facets_include='brand:15', facets_enabled=True)
  response = request.execute()

  # Pick the first and only facet for this query
  facet = response['facets'][0]

  print('\n\tHistogram for "%s":\n' % facet['property'])

  labels = []
  values = []

  for bucket in facet['buckets']:
    labels.append(bucket['value'].rjust(20))
    values.append(bucket['count'])

  weighting = 50.0 / max(values)

  for label, value in zip(labels, values):
    print(label, '#' * int(weighting * value), '(%s)' % value)

  print()


if __name__ == '__main__':
    main()
