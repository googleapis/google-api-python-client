"""Notification channels tests."""
from __future__ import absolute_import

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import unittest2 as unittest
import datetime

from googleapiclient import channel
from googleapiclient import errors


class TestChannel(unittest.TestCase):
  def test_basic(self):
    ch = channel.Channel('web_hook', 'myid', 'mytoken',
                         'http://example.org/callback',
                         expiration=0,
                         params={'extra': 'info'},
                         resource_id='the_resource_id',
                         resource_uri='http://example.com/resource_1')

    # Converting to a body.
    body = ch.body()
    self.assertEqual('http://example.org/callback', body['address'])
    self.assertEqual('myid', body['id'])
    self.assertEqual('missing', body.get('expiration', 'missing'))
    self.assertEqual('info', body['params']['extra'])
    self.assertEqual('the_resource_id', body['resourceId'])
    self.assertEqual('http://example.com/resource_1', body['resourceUri'])
    self.assertEqual('web_hook', body['type'])

    # Converting to a body with expiration set.
    ch.expiration = 1
    body = ch.body()
    self.assertEqual(1, body.get('expiration', 'missing'))

    # Converting to a body after updating with a response body.
    ch.update({
        'resourceId': 'updated_res_id',
        'resourceUri': 'updated_res_uri',
        'some_random_parameter': 2,
        })

    body = ch.body()
    self.assertEqual('http://example.org/callback', body['address'])
    self.assertEqual('myid', body['id'])
    self.assertEqual(1, body.get('expiration', 'missing'))
    self.assertEqual('info', body['params']['extra'])
    self.assertEqual('updated_res_id', body['resourceId'])
    self.assertEqual('updated_res_uri', body['resourceUri'])
    self.assertEqual('web_hook', body['type'])

  def test_new_webhook_channel(self):
    ch = channel.new_webhook_channel('http://example.com/callback')
    self.assertEqual(0, ch.expiration)
    self.assertEqual('http://example.com/callback', ch.address)
    self.assertEqual(None, ch.params)

    # New channel with an obviously wrong expiration time.
    ch = channel.new_webhook_channel(
        'http://example.com/callback',
        expiration=datetime.datetime(1965, 1, 1))
    self.assertEqual(0, ch.expiration)

    # New channel with an expiration time.
    ch = channel.new_webhook_channel(
        'http://example.com/callback',
        expiration=datetime.datetime(1970, 1, 1, second=5))
    self.assertEqual(5000, ch.expiration)
    self.assertEqual('http://example.com/callback', ch.address)
    self.assertEqual(None, ch.params)

    # New channel with an expiration time and params.
    ch = channel.new_webhook_channel(
        'http://example.com/callback',
        expiration=datetime.datetime(1970, 1, 1, second=5, microsecond=1000),
        params={'some':'stuff'})
    self.assertEqual(5001, ch.expiration)
    self.assertEqual('http://example.com/callback', ch.address)
    self.assertEqual({'some': 'stuff'}, ch.params)


class TestNotification(unittest.TestCase):
  def test_basic(self):
    n = channel.Notification(12, 'sync', 'http://example.org',
                     'http://example.org/v1')

    self.assertEqual(12, n.message_number)
    self.assertEqual('sync', n.state)
    self.assertEqual('http://example.org', n.resource_uri)
    self.assertEqual('http://example.org/v1', n.resource_id)

  def test_notification_from_headers(self):
    headers = {
        'X-GoOG-CHANNEL-ID': 'myid',
        'X-Goog-MESSAGE-NUMBER': '1',
        'X-Goog-rESOURCE-STATE': 'sync',
        'X-Goog-reSOURCE-URI': 'http://example.com/',
        'X-Goog-resOURCE-ID': 'http://example.com/resource_1',
        }

    ch = channel.Channel('web_hook', 'myid', 'mytoken',
                         'http://example.org/callback',
                         expiration=0,
                         params={'extra': 'info'},
                         resource_id='the_resource_id',
                         resource_uri='http://example.com/resource_1')

    # Good test case.
    n = channel.notification_from_headers(ch, headers)
    self.assertEqual('http://example.com/resource_1', n.resource_id)
    self.assertEqual('http://example.com/', n.resource_uri)
    self.assertEqual('sync', n.state)
    self.assertEqual(1, n.message_number)

    # Detect id mismatch.
    ch.id = 'different_id'
    try:
      n = channel.notification_from_headers(ch, headers)
      self.fail('Should have raised exception')
    except errors.InvalidNotificationError:
      pass

    # Set the id back to a correct value.
    ch.id = 'myid'
