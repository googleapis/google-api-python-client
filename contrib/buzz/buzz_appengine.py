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
import simple_wrapper


class Flow(db.Model):
  flow = apiclient.ext.appengine.FlowThreeLeggedProperty()


class Credentials(db.Model):
  credentials = apiclient.ext.appengine.OAuthCredentialsProperty()


class oauth_required(object):
  def __init__(self, *decorator_args, **decorator_kwargs):
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
    self.decorator_args = decorator_args
    self.decorator_kwargs = decorator_kwargs

  def __load_settings_from_file__(self):
    # Load settings from settings.py module if it's available
    # Only return the keys that the user has explicitly set
    try:
      import settings
      
      # This uses getattr so that the user can set just the parameters they care about
      flow_settings = {
      'consumer_key' : getattr(settings, 'CONSUMER_KEY', None),
      'consumer_secret' :  getattr(settings, 'CONSUMER_SECRET', None),
      'user_agent' :  getattr(settings, 'USER_AGENT', None),
      'domain' :  getattr(settings, 'DOMAIN', None),
      'scope' :  getattr(settings, 'SCOPE', None),
      'xoauth_display_name' :  getattr(settings, 'XOAUTH_DISPLAY_NAME', None)
      }
      
      # Strip out all the keys that weren't specified in the settings.py
      # This is needed to ensure that those keys don't override what's 
      # specified in the decorator invocation
      cleaned_flow_settings = {}
      for key,value in flow_settings.items():
        if value is not None:
          cleaned_flow_settings[key] = value
      
      return cleaned_flow_settings
    except ImportError:
      return {}

  def __load_settings__(self):
    # Set up the default arguments and override them with whatever values have been given to the decorator
    flow_settings = {
    'consumer_key' : 'anonymous',
    'consumer_secret' : 'anonymous',
    'user_agent' : 'google-api-client-python-buzz-webapp/1.0',
    'domain' : 'anonymous',
    'scope' : 'https://www.googleapis.com/auth/buzz',
    'xoauth_display_name' : 'Default Display Name For OAuth Application'
    }
    logging.info('OAuth settings: %s ' % flow_settings)
    
    # Override the defaults with whatever the user may have put into settings.py
    settings_kwargs = self.__load_settings_from_file__()
    flow_settings.update(settings_kwargs)
    logging.info('OAuth settings: %s ' % flow_settings)
    
    # Override the defaults with whatever the user have specified in the decorator's invocation
    flow_settings.update(self.decorator_kwargs)
    logging.info('OAuth settings: %s ' % flow_settings)
    return flow_settings
  
  def __call__(self, handler_method):
    def check_oauth_credentials_wrapper(*args, **kwargs):
      handler_instance = args[0]
      # TODO(ade) Add support for POST requests
      if handler_instance.request.method != 'GET':
        raise webapp.Error('The check_oauth decorator can only be used for GET '
                           'requests')

      # Is this a request from the OAuth system after finishing the OAuth dance?
      if handler_instance.request.get('oauth_verifier'):
        user = users.get_current_user()
        logging.debug('Finished OAuth dance for: %s' % user.email())

        f = Flow.get_by_key_name(user.user_id())
        if f:
          credentials = f.flow.step2_exchange(handler_instance.request.params)
          c = Credentials(key_name=user.user_id(), credentials=credentials)
          c.put()
        
          # We delete the flow so that a malicious actor can't pretend to be the OAuth service
          # and replace a valid token with an invalid token
          f.delete()
          
          handler_method(*args)
          return 

      # Find out who the user is. If we don't know who you are then we can't 
      # look up your OAuth credentials thus we must ensure the user is logged in.
      user = users.get_current_user()
      if not user:
        handler_instance.redirect(users.create_login_url(handler_instance.request.uri))
        return
    
      # Now that we know who the user is look up their OAuth credentials
      # if we don't find the credentials then send them through the OAuth dance
      if not Credentials.get_by_key_name(user.user_id()):
        flow_settings = self.__load_settings__()
        
        p = apiclient.discovery.build("buzz", "v1")
        flow = apiclient.oauth.FlowThreeLegged(p.auth_discovery(),
                                              consumer_key=flow_settings['consumer_key'],
                                              consumer_secret=flow_settings['consumer_secret'],
                                              user_agent=flow_settings['user_agent'],
                                              domain=flow_settings['domain'],
                                              scope=flow_settings['scope'],
                                              xoauth_displayname=flow_settings['xoauth_display_name'])

        # The OAuth system needs to send the user right back here so that they
        # get to the page they originally intended to visit.
        oauth_return_url = handler_instance.request.uri
        authorize_url = flow.step1_get_authorize_url(oauth_return_url)
      
        f = Flow(key_name=user.user_id(), flow=flow)
        f.put()
      
        handler_instance.redirect(authorize_url)
        return
    
      # If the user already has a token then call the wrapped handler
      handler_method(*args)
    return check_oauth_credentials_wrapper

def build_buzz_wrapper_for_current_user(api_key=None):
  user = users.get_current_user()
  credentials = Credentials.get_by_key_name(user.user_id()).credentials
  if not api_key:
    try:
      import settings
      api_key = getattr(settings, 'API_KEY', None)
    except ImportError:
      return {}
  return simple_wrapper.SimpleWrapper(api_key=api_key, 
                                                 credentials=credentials)