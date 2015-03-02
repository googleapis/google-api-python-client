#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Google Inc. All Rights Reserved.

"""Query that is restricted by a parameter against the public shopping search
API"""

import pprint

from googleapiclient.discovery import build


SHOPPING_API_VERSION = 'v1'
DEVELOPER_KEY = 'AIzaSyACZJW4JwcWwz5taR2gjIMNQrtgDLfILPc'


def main():
  """Get and print a feed of all public products matching the search query
  "digital camera", that are created by "Canon" available in the
  United States.

  The "restrictBy" parameter controls which types of results are returned.

  Multiple values for a single restrictBy can be separated by the "|" operator,
  so to look for all products created by Canon, Sony, or Apple:

  restrictBy = 'brand:canon|sony|apple'

  Multiple restricting parameters should be separated by a comma, so for
  products created by Sony with the word "32GB" in the title:

  restrictBy = 'brand:sony,title:32GB'
  """
  client = build('shopping', SHOPPING_API_VERSION, developerKey=DEVELOPER_KEY)
  resource = client.products()
  request = resource.list(source='public', country='US',
                          restrictBy='brand:canon', q='Digital Camera')
  response = request.execute()
  pprint.pprint(response)


if __name__ == '__main__':
    main()
