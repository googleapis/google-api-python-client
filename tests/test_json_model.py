#!/usr/bin/python2.4
#
# Copyright 2010 Google Inc. All Rights Reserved.

"""Discovery document tests

Unit tests for objects created from discovery documents.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

from apiclient.discovery import JsonModel
import os
import unittest


class Model(unittest.TestCase):
  def test_json_no_body(self):
    model = JsonModel()

    headers = {}
    path_params = {}
    query_params = {}
    body = None

    headers, params, query, body = model.request(headers, path_params, query_params, body)

    self.assertEqual(headers['accept'], 'application/json')
    self.assertTrue('content-type' not in headers)
    self.assertNotEqual(query, '')
    self.assertEqual(body, None)

  def test_json_body(self):
    model = JsonModel()

    headers = {}
    path_params = {}
    query_params = {}
    body = {}

    headers, params, query, body = model.request(headers, path_params, query_params, body)

    self.assertEqual(headers['accept'], 'application/json')
    self.assertEqual(headers['content-type'], 'application/json')
    self.assertNotEqual(query, '')
    self.assertEqual(body, '{"data": {}}')

if __name__ == '__main__':
  unittest.main()
