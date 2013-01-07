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

"""Push notifications support.

This code is based on experimental APIs and is subject to change.
"""

__author__ = 'afshar@google.com (Ali Afshar)'

import binascii
import collections
import os
import urllib

SUBSCRIBE = 'X-GOOG-SUBSCRIBE'
SUBSCRIPTION_ID = 'X-GOOG-SUBSCRIPTION-ID'
TOPIC_ID = 'X-GOOG-TOPIC-ID'
TOPIC_URI = 'X-GOOG-TOPIC-URI'
CLIENT_TOKEN = 'X-GOOG-CLIENT-TOKEN'
EVENT_TYPE = 'X-GOOG-EVENT-TYPE'
UNSUBSCRIBE = 'X-GOOG-UNSUBSCRIBE'


class InvalidSubscriptionRequestError(ValueError):
  """The request cannot be subscribed."""


def new_token():
  """Gets a random token for use as a client_token in push notifications.

  Returns:
    str, a new random token.
  """
  return binascii.hexlify(os.urandom(32))


class Channel(object):
  """Base class for channel types."""

  def __init__(self, channel_type, channel_args):
    """Create a new Channel.

    You probably won't need to create this channel manually, since there are
    subclassed Channel for each specific type with a more customized set of
    arguments to pass. However, you may wish to just create it manually here.

    Args:
      channel_type: str, the type of channel.
      channel_args: dict, arguments to pass to the channel.
    """
    self.channel_type = channel_type
    self.channel_args = channel_args

  def as_header_value(self):
    """Create the appropriate header for this channel.

    Returns:
      str encoded channel description suitable for use as a header.
    """
    return '%s?%s' % (self.channel_type, urllib.urlencode(self.channel_args))

  def write_header(self, headers):
    """Write the appropriate subscribe header to a headers dict.

    Args:
      headers: dict, headers to add subscribe header to.
    """
    headers[SUBSCRIBE] = self.as_header_value()


class WebhookChannel(Channel):
  """Channel for registering web hook notifications."""

  def __init__(self, url, app_engine=False):
    """Create a new WebhookChannel

    Args:
      url: str, URL to post notifications to.
      app_engine: bool, default=False, whether the destination for the
      notifications is an App Engine application.
    """
    super(WebhookChannel, self).__init__(
        channel_type='web_hook',
        channel_args={
            'url': url,
            'app_engine': app_engine and 'true' or 'false',
        }
    )


class Headers(collections.defaultdict):
  """Headers for managing subscriptions."""


  ALL_HEADERS = set([SUBSCRIBE, SUBSCRIPTION_ID, TOPIC_ID, TOPIC_URI,
                     CLIENT_TOKEN, EVENT_TYPE, UNSUBSCRIBE])

  def __init__(self):
    """Create a new subscription configuration instance."""
    collections.defaultdict.__init__(self, str)

  def __setitem__(self, key, value):
    """Set a header value, ensuring the key is an allowed value.

    Args:
      key: str, the header key.
      value: str, the header value.
    Raises:
      ValueError if key is not one of the accepted headers.
    """
    normal_key = self._normalize_key(key)
    if normal_key not in self.ALL_HEADERS:
      raise ValueError('Header name must be one of %s.' % self.ALL_HEADERS)
    else:
      return collections.defaultdict.__setitem__(self, normal_key, value)

  def __getitem__(self, key):
    """Get a header value, normalizing the key case.

    Args:
      key: str, the header key.
    Returns:
      String header value.
    Raises:
      KeyError if the key is not one of the accepted headers.
    """
    normal_key = self._normalize_key(key)
    if normal_key not in self.ALL_HEADERS:
      raise ValueError('Header name must be one of %s.' % self.ALL_HEADERS)
    else:
      return collections.defaultdict.__getitem__(self, normal_key)

  def _normalize_key(self, key):
    """Normalize a header name for use as a key."""
    return key.upper()

  def items(self):
    """Generator for each header."""
    for header in self.ALL_HEADERS:
      value = self[header]
      if value:
        yield header, value

  def write(self, headers):
    """Applies the subscription headers.

    Args:
      headers: dict of headers to insert values into.
    """
    for header, value in self.items():
      headers[header.lower()] = value

  def read(self, headers):
    """Read from headers.

    Args:
      headers: dict of headers to read from.
    """
    for header in self.ALL_HEADERS:
      if header.lower() in headers:
        self[header] = headers[header.lower()]


class Subscription(object):
  """Information about a subscription."""

  def __init__(self):
    """Create a new Subscription."""
    self.headers = Headers()

  @classmethod
  def for_request(cls, request, channel, client_token=None):
    """Creates a subscription and attaches it to a request.

    Args:
      request: An http.HttpRequest to modify for making a subscription.
      channel: A apiclient.push.Channel describing the subscription to
               create.
      client_token: (optional) client token to verify the notification.

    Returns:
      New subscription object.
    """
    subscription = cls.for_channel(channel=channel, client_token=client_token)
    subscription.headers.write(request.headers)
    if request.method != 'GET':
      raise InvalidSubscriptionRequestError(
          'Can only subscribe to requests which are GET.')
    request.method = 'POST'

    def _on_response(response, subscription=subscription):
      """Called with the response headers. Reads the subscription headers."""
      subscription.headers.read(response)

    request.add_response_callback(_on_response)
    return subscription

  @classmethod
  def for_channel(cls, channel, client_token=None):
    """Alternate constructor to create a subscription from a channel.

    Args:
      channel: A apiclient.push.Channel describing the subscription to
               create.
      client_token: (optional) client token to verify the notification.

    Returns:
      New subscription object.
    """
    subscription = cls()
    channel.write_header(subscription.headers)
    if client_token is None:
      client_token = new_token()
    subscription.headers[SUBSCRIPTION_ID] = new_token()
    subscription.headers[CLIENT_TOKEN] = client_token
    return subscription

  def verify(self, headers):
    """Verifies that a webhook notification has the correct client_token.

    Args:
      headers: dict of request headers for a push notification.

    Returns:
      Boolean value indicating whether the notification is verified.
    """
    new_subscription = Subscription()
    new_subscription.headers.read(headers)
    return new_subscription.client_token == self.client_token

  @property
  def subscribe(self):
    """Subscribe header value."""
    return self.headers[SUBSCRIBE]

  @property
  def subscription_id(self):
    """Subscription ID header value."""
    return self.headers[SUBSCRIPTION_ID]

  @property
  def topic_id(self):
    """Topic ID header value."""
    return self.headers[TOPIC_ID]

  @property
  def topic_uri(self):
    """Topic URI header value."""
    return self.headers[TOPIC_URI]

  @property
  def client_token(self):
    """Client Token header value."""
    return self.headers[CLIENT_TOKEN]

  @property
  def event_type(self):
    """Event Type header value."""
    return self.headers[EVENT_TYPE]

  @property
  def unsubscribe(self):
    """Unsuscribe header value."""
    return self.headers[UNSUBSCRIBE]
