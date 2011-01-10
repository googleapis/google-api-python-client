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

from google.appengine.api import users
from google.appengine.ext import db

import apiclient.ext.appengine
import logging
import settings
import simple_buzz_wrapper


class Flow(db.Model):
  flow = apiclient.ext.appengine.FlowThreeLeggedProperty()


class Credentials(db.Model):
  credentials = apiclient.ext.appengine.OAuthCredentialsProperty()


def oauth_required(handler_method):
  """A decorator to require that a user has gone through the OAuth dance before accessing a handler.
  
  To use it, decorate your get() method like this:
    @oauth_required
    def get(self):
      buzz_wrapper = oauth_handlers.build_buzz_wrapper_for_current_user()
      user_profile_data = buzz_wrapper.get_profile()
      self.response.out.write('Hello, ' + user_profile_data.displayName)
  
  We will redirect the user to the OAuth endpoint and afterwards the OAuth
  will send the user back to the DanceFinishingHandler that you have configured.
  This should only used for GET requests since any payload in a POST request
  will be lost. Any parameters in the original URL will be preserved.
  """
  def check_oauth_credentials(self, *args):
    if self.request.method != 'GET':
      raise webapp.Error('The check_oauth decorator can only be used for GET '
                         'requests')

    # Is this a request from the OAuth system after finishing the OAuth dance?
    if self.request.get('oauth_verifier'):
      user = users.get_current_user()
      logging.debug('Finished OAuth dance for: %s' % user.email())

      f = Flow.get_by_key_name(user.user_id())
      if f:
        credentials = f.flow.step2_exchange(self.request.params)
        c = Credentials(key_name=user.user_id(), credentials=credentials)
        c.put()
        
        # We delete the flow so that a malicious actor can't pretend to be the OAuth service
        # and replace a valid token with an invalid token
        f.delete()
      handler_method(self, *args)
      return 

    # Find out who the user is. If we don't know who you are then we can't 
    # look up your OAuth credentials thus we must ensure the user is logged in.
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.uri))
      return
    
    # Now that we know who the user is look up their OAuth credentials
    # if we don't find the credentials then send them through the OAuth dance
    if not Credentials.get_by_key_name(user.user_id()):
      # TODO(ade) make this more configurable using settings.py
      # Domain, and scope should be configurable
      p = apiclient.discovery.build("buzz", "v1")
      flow = apiclient.oauth.FlowThreeLegged(p.auth_discovery(),
                     consumer_key=settings.CONSUMER_KEY,
                     consumer_secret=settings.CONSUMER_SECRET,
                     user_agent='google-api-client-python-buzz-webapp/1.0',
                     domain='anonymous',
                     scope='https://www.googleapis.com/auth/buzz',
                     xoauth_displayname=settings.DISPLAY_NAME)

      # The OAuth system needs to send the user right back here so that they
      # get to the page they originally intended to visit.
      oauth_return_url = self.request.uri
      authorize_url = flow.step1_get_authorize_url(oauth_return_url)
      
      f = Flow(key_name=user.user_id(), flow=flow)
      f.put()
      
      self.redirect(authorize_url)
      return
    
    # If the user already has a token then call the wrapped handler
    handler_method(self, *args)
  return check_oauth_credentials

def build_buzz_wrapper_for_current_user():
  user = users.get_current_user()
  credentials = Credentials.get_by_key_name(user.user_id()).credentials
  return simple_buzz_wrapper.SimpleBuzzWrapper(api_key=settings.API_KEY, 
                                                 credentials=credentials)