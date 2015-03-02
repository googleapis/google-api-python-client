#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Google Inc. All Rights Reserved.

"""Full text search query against the shopping search API"""

import pprint

from googleapiclient.discovery import build


SHOPPING_API_VERSION = 'v1'
DEVELOPER_KEY = 'AIzaSyACZJW4JwcWwz5taR2gjIMNQrtgDLfILPc'


def main():
  """Get and print a feed of all public products matching the search query
  "digital camera".

  This is achieved by using the q query parameter to the list method.

  The "|" operator can be used to search for alternative search terms, for
  example: q = 'banana|apple' will search for bananas or apples.

  Search phrases such as those containing spaces can be specified by
  surrounding them with double quotes, for example q='"mp3 player"'. This can
  be useful when combining with the "|" operator such as q = '"mp3
  player"|ipod'.
  """
  client = build('shopping', SHOPPING_API_VERSION, developerKey=DEVELOPER_KEY)
  resource = client.products()
  # Note the 'q' parameter, which will contain the value of the search query
  request = resource.list(source='public', country='US', q=u'digital camera')
  response = request.execute()
  pprint.pprint(response)


if __name__ == '__main__':
    main()
