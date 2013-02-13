# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Push notifications tests."""

__author__ = 'afshar@google.com (Ali Afshar)'

import unittest

from apiclient import push
from apiclient import model
from apiclient import http
from test_discovery import assertUrisEqual


class ClientTokenGeneratorTest(unittest.TestCase):

  def test_next(self):
    t = push.new_token()
    self.assertTrue(t)


class ChannelTest(unittest.TestCase):

  def test_creation_noargs(self):
    c = push.Channel(channel_type='my_channel_type', channel_args={})
    self.assertEqual('my_channel_type', c.channel_type)
    self.assertEqual({}, c.channel_args)

  def test_creation_args(self):
    c = push.Channel(channel_type='my_channel_type',
                         channel_args={'a': 'b'})
    self.assertEqual('my_channel_type', c.channel_type)
    self.assertEqual({'a':'b'}, c.channel_args)

  def test_as_header_value_noargs(self):
    c = push.Channel(channel_type='my_channel_type', channel_args={})
    self.assertEqual('my_channel_type?', c.as_header_value())

  def test_as_header_value_args(self):
    c = push.Channel(channel_type='my_channel_type',
                         channel_args={'a': 'b'})
    self.assertEqual('my_channel_type?a=b', c.as_header_value())

  def test_as_header_value_args_space(self):
    c = push.Channel(channel_type='my_channel_type',
                         channel_args={'a': 'b c'})
    self.assertEqual('my_channel_type?a=b+c', c.as_header_value())

  def test_as_header_value_args_escape(self):
    c = push.Channel(channel_type='my_channel_type',
                         channel_args={'a': 'b%c'})
    self.assertEqual('my_channel_type?a=b%25c', c.as_header_value())

  def test_write_header_noargs(self):
    c = push.Channel(channel_type='my_channel_type', channel_args={})
    headers = {}
    c.write_header(headers)
    self.assertEqual('my_channel_type?', headers['X-GOOG-SUBSCRIBE'])

  def test_write_header_args(self):
    c = push.Channel(channel_type='my_channel_type',
                         channel_args={'a': 'b'})
    headers = {}
    c.write_header(headers)
    self.assertEqual('my_channel_type?a=b', headers['X-GOOG-SUBSCRIBE'])

  def test_write_header_args_space(self):
    c = push.Channel(channel_type='my_channel_type',
                         channel_args={'a': 'b c'})
    headers = {}
    c.write_header(headers)
    self.assertEqual('my_channel_type?a=b+c', headers['X-GOOG-SUBSCRIBE'])

  def test_write_header_args_escape(self):
    c = push.Channel(channel_type='my_channel_type',
                         channel_args={'a': 'b%c'})
    headers = {}
    c.write_header(headers)
    self.assertEqual('my_channel_type?a=b%25c', headers['X-GOOG-SUBSCRIBE'])


class WebhookChannelTest(unittest.TestCase):

  def test_creation_no_appengine(self):
    c = push.WebhookChannel('http://example.org')
    assertUrisEqual(self,
                    'web_hook?url=http%3A%2F%2Fexample.org&app_engine=false',
                    c.as_header_value())

  def test_creation_appengine(self):
    c = push.WebhookChannel('http://example.org', app_engine=True)
    assertUrisEqual(self,
                    'web_hook?url=http%3A%2F%2Fexample.org&app_engine=true',
                    c.as_header_value())


class HeadersTest(unittest.TestCase):

  def test_creation(self):
    h = push.Headers()
    self.assertEqual('', h[push.SUBSCRIBE])

  def test_items(self):
    h = push.Headers()
    h[push.SUBSCRIBE] = 'my_channel_type'
    self.assertEqual([(push.SUBSCRIBE, 'my_channel_type')], list(h.items()))

  def test_items_non_whitelisted(self):
    h = push.Headers()
    def set_bad_header(h=h):
      h['X-Banana'] = 'my_channel_type'
    self.assertRaises(ValueError, set_bad_header)

  def test_read(self):
    h = push.Headers()
    h.read({'x-goog-subscribe': 'my_channel_type'})
    self.assertEqual([(push.SUBSCRIBE, 'my_channel_type')], list(h.items()))

  def test_read_non_whitelisted(self):
    h = push.Headers()
    h.read({'X-Banana': 'my_channel_type'})
    self.assertEqual([], list(h.items()))

  def test_write(self):
    h = push.Headers()
    h[push.SUBSCRIBE] = 'my_channel_type'
    headers = {}
    h.write(headers)
    self.assertEqual({'x-goog-subscribe': 'my_channel_type'}, headers)


class SubscriptionTest(unittest.TestCase):

  def test_create(self):
    s = push.Subscription()
    self.assertEqual('', s.client_token)

  def test_create_for_channnel(self):
    c = push.WebhookChannel('http://example.org')
    s = push.Subscription.for_channel(c)
    self.assertTrue(s.client_token)
    assertUrisEqual(self,
                    'web_hook?url=http%3A%2F%2Fexample.org&app_engine=false',
                    s.subscribe)

  def test_create_for_channel_client_token(self):
    c = push.WebhookChannel('http://example.org')
    s = push.Subscription.for_channel(c, client_token='my_token')
    self.assertEqual('my_token', s.client_token)
    assertUrisEqual(self,
                    'web_hook?url=http%3A%2F%2Fexample.org&app_engine=false',
                    s.subscribe)

  def test_subscribe(self):
    s = push.Subscription()
    s.headers[push.SUBSCRIBE] = 'my_header'
    self.assertEqual('my_header', s.subscribe)

  def test_subscription_id(self):
    s = push.Subscription()
    s.headers[push.SUBSCRIPTION_ID] = 'my_header'
    self.assertEqual('my_header', s.subscription_id)

  def test_subscription_id_set(self):
    c = push.WebhookChannel('http://example.org')
    s = push.Subscription.for_channel(c)
    self.assertTrue(s.subscription_id)

  def test_topic_id(self):
    s = push.Subscription()
    s.headers[push.TOPIC_ID] = 'my_header'
    self.assertEqual('my_header', s.topic_id)

  def test_topic_uri(self):
    s = push.Subscription()
    s.headers[push.TOPIC_URI] = 'my_header'
    self.assertEqual('my_header', s.topic_uri)

  def test_client_token(self):
    s = push.Subscription()
    s.headers[push.CLIENT_TOKEN] = 'my_header'
    self.assertEqual('my_header', s.client_token)

  def test_event_type(self):
    s = push.Subscription()
    s.headers[push.EVENT_TYPE] = 'my_header'
    self.assertEqual('my_header', s.event_type)

  def test_unsubscribe(self):
    s = push.Subscription()
    s.headers[push.UNSUBSCRIBE] = 'my_header'
    self.assertEqual('my_header', s.unsubscribe)

  def test_do_subscribe(self):
    m = model.JsonModel()
    request = http.HttpRequest(
        None,
        m.response,
        'https://www.googleapis.com/someapi/v1/collection/?foo=bar',
        method='GET',
        body='{}',
        headers={'content-type': 'application/json'})
    h = http.HttpMockSequence([
        ({'status': 200,
          'X-Goog-Subscription-ID': 'my_subscription'},
          '{}')])
    c = push.Channel('my_channel', {})
    s = push.Subscription.for_request(request, c)
    request.execute(http=h)
    self.assertEqual('my_subscription', s.subscription_id)

  def test_subscribe_with_token(self):
    m = model.JsonModel()
    request = http.HttpRequest(
        None,
        m.response,
        'https://www.googleapis.com/someapi/v1/collection/?foo=bar',
        method='GET',
        body='{}',
        headers={'content-type': 'application/json'})
    h = http.HttpMockSequence([
        ({'status': 200,
          'X-Goog-Subscription-ID': 'my_subscription'},
          '{}')])
    c = push.Channel('my_channel', {})
    s = push.Subscription.for_request(request, c, client_token='my_token')
    request.execute(http=h)
    self.assertEqual('my_subscription', s.subscription_id)
    self.assertEqual('my_token', s.client_token)

  def test_verify_good_token(self):
    s = push.Subscription()
    s.headers['X-Goog-Client-Token'] = '123'
    notification_headers = {'x-goog-client-token': '123'}
    self.assertTrue(s.verify(notification_headers))

  def test_verify_bad_token(self):
    s = push.Subscription()
    s.headers['X-Goog-Client-Token'] = '321'
    notification_headers = {'x-goog-client-token': '123'}
    self.assertFalse(s.verify(notification_headers))

  def test_request_is_post(self):
    m = model.JsonModel()
    request = http.HttpRequest(
        None,
        m.response,
        'https://www.googleapis.com/someapi/v1/collection/?foo=bar',
        method='GET',
        body='{}',
        headers={'content-type': 'application/json'})
    c = push.Channel('my_channel', {})
    push.Subscription.for_request(request, c)
    self.assertEqual('POST', request.method)

  def test_non_get_error(self):
    m = model.JsonModel()
    request = http.HttpRequest(
        None,
        m.response,
        'https://www.googleapis.com/someapi/v1/collection/?foo=bar',
        method='POST',
        body='{}',
        headers={'content-type': 'application/json'})
    c = push.Channel('my_channel', {})
    self.assertRaises(push.InvalidSubscriptionRequestError,
                      push.Subscription.for_request, request, c)
