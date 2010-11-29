# Copyright (C) 2010 Google Inc.
#
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

__author__ = 'ade@google.com'

import buzz_gae_client
import unittest

class BuzzGaeClientTest(unittest.TestCase):
    def test_can_build_client(self):
      client = buzz_gae_client.BuzzGaeClient()
      self.assertNotEquals(None, client)

    def test_can_get_request_token(self):
        client = buzz_gae_client.BuzzGaeClient()
        callback_url = 'http://example.com'
        request_token = client.get_request_token(callback_url)
        self.assertTrue(request_token['oauth_token'] is not None)
        self.assertTrue(request_token['oauth_token_secret'] is not None)
        self.assertEquals(request_token['oauth_callback_confirmed'], 'true')

    def test_can_generate_authorisation_url(self):
        client = buzz_gae_client.BuzzGaeClient()
        callback_url = 'http://example.com'
        request_token = client.get_request_token(callback_url)
        authorisation_url = client.generate_authorisation_url(request_token)
        self.assertTrue(authorisation_url is not None)
        self.assertTrue(authorisation_url.startswith('https://www.google.com/buzz/api/auth/OAuthAuthorizeToken?scope='))

    # TODO(ade) this test can't work outside of the AppEngine environment. Find an equivalent that works.
    def _test_can_upgrade_tokens(self):
      client = buzz_gae_client.BuzzGaeClient()
      callback_url = 'http://example.com'
      request_token = client.get_request_token(callback_url)
      oauth_verifier = 'some verifier'

      consumer_key = 'anonymous'
      consumer_secret = 'anonymous'
      usable_token = client.upgrade_to_access_token(request_token, oauth_verifier)
      self.assertTrue(usable_token is not None)
      self.assertEquals(consumer_key, usable_token['consumer_key'])
      self.assertEquals(consumer_secret, usable_token['consumer_secret'])
      self.assertTrue(usable_token['access_token'] is not None)

    def test_can_build_apiclient_with_access_token(self):
      client = buzz_gae_client.BuzzGaeClient()
      oauth_parameters = {}
      oauth_parameters['oauth_token'] = ''
      oauth_parameters['oauth_token_secret'] = ''
      oauth_parameters['consumer_key'] = ''
      oauth_parameters['consumer_secret'] = ''
      api_client = client.build_api_client(oauth_parameters)
      self.assertTrue(api_client is not None)

    def test_can_fetch_activites_from_buzz(self):
      client = buzz_gae_client.BuzzGaeClient()
      api_client = client.build_api_client()
      count = 9
      activities = api_client.activities().list(userId='googlebuzz', scope='@self', max_results=count)['items']
      self.assertEquals(count, len(activities))

if __name__ == '__main__':
  unittest.main()
