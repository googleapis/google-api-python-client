#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Google Inc. All Rights Reserved.

'''Simple command-line example for The Google Search
API for Shopping.

Command-line application that does a search for products.
'''
from __future__ import print_function

__author__ = 'aherrman@google.com (Andy Herrman)'

from googleapiclient.discovery import build

# Uncomment the next line to get very detailed logging
# httplib2.debuglevel = 4


def main():
  p = build('shopping', 'v1',
            developerKey='AIzaSyDRRpR3GS1F1_jKNNM9HCNd2wJQyPG3oN0')

  # Search over all public offers:
  print('Searching all public offers.')
  res = p.products().list(
      country='US',
      source='public',
      q='android t-shirt'
      ).execute()
  print_items(res['items'])

  # Search over a specific merchant's offers:
  print()
  print('Searching Google Store.')
  res = p.products().list(
      country='US',
      source='public',
      q='android t-shirt',
      restrictBy='accountId:5968952',
      ).execute()
  print_items(res['items'])

  # Remember the Google Id of the last product
  googleId = res['items'][0]['product']['googleId']

  # Get data for the single public offer:
  print()
  print('Getting data for offer %s' % googleId)
  res = p.products().get(
      source='public',
      accountId='5968952',
      productIdType='gid',
      productId=googleId
      ).execute()
  print_item(res)


def print_item(item):
  """Displays a single item: title, merchant, link."""
  product = item['product']
  print('- %s [%s] (%s)' % (product['title'],
                          product['author']['name'],
                          product['link']))


def print_items(items):
  """Displays a number of items."""
  for item in items:
    print_item(item)

if __name__ == '__main__':
  main()
