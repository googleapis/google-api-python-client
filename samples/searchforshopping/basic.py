#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Google Inc. All Rights Reserved.

"""Basic query against the public shopping search API"""

import pprint

from googleapiclient.discovery import build


SHOPPING_API_VERSION = 'v1'
DEVELOPER_KEY = 'AIzaSyACZJW4JwcWwz5taR2gjIMNQrtgDLfILPc'


def main():
  """Get and print a feed of all public products available in the
  United States.

  Note: The source and country arguments are required to pass to the list
  method.
  """
  client = build('shopping', SHOPPING_API_VERSION, developerKey=DEVELOPER_KEY)
  resource = client.products()
  request = resource.list(source='public', country='US')
  response = request.execute()
  pprint.pprint(response)


if __name__ == '__main__':
    main()
