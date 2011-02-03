#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
#
# Copyright 2010 Google Inc. All Rights Reserved.

'''Simple command-line example for The Google Search
API for Shopping.

Command-line application that does a search for products.
'''

__author__ = 'aherrman@google.com (Andy Herrman)'

from apiclient.discovery import build

# Uncomment the next line to get very detailed logging
# httplib2.debuglevel = 4


def main():
  p = build('shopping', 'v1',
            developerKey='AIzaSyDRRpR3GS1F1_jKNNM9HCNd2wJQyPG3oN0')

  # Search over all public offers:
  print 'Searching all public offers.'
  res = p.products().list(
      country='US',
      source='public',
      q='android tshirt'
      ).execute()
  print_items(res['items'])

  # Search over a specific merchant's offers:
  print
  print 'Searching Google Store.'
  res = p.products().list(
      country='US',
      source='mc:5968952',
      q='android tshirt'
      ).execute()
  print_items(res['items'])

  # Get data for a single public offer:
  print
  print 'Getting data for offer 8749318160742051003'
  res = p.products().get(
      source='mc:5968952',
      accountId='5968952',
      productIdType='gid',
      productId='8749318160742051003'
      ).execute()
  print_item(res)


def print_item(item):
  product = item['product']
  print '%s (%s)' % (product['title'], product['link'])


def print_items(items):
  for item in items:
    print_item(item)

if __name__ == '__main__':
  main()
