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
from apiclient.discovery import build
from apiclient.oauth import FlowThreeLegged

import datetime
import httplib2
import logging
import oauth_wrap
import optparse
import os
import sys


def load_properties_file(path):
  properties = {}
  for line in open(path):
    line = line.strip()
    if line.startswith('#'):
      continue
      
    key,value = line.split('=')
    properties[key.strip()] = value.strip()
  return properties


def save_properties(consumer_key, consumer_secret, token_key, token_secret, path):
  file = open(path, 'w')
  
  # File format and order is based on oacurl.java's defaults
  now = datetime.datetime.today()
  now_string = now.strftime('%a %b %d %H:%m:%S %Z %Y')
  file.write('#%s\n' % now_string)
  file.write('consumerSecret=%s\n' % consumer_secret)
  file.write('accessToken=%s\n' % token_key)
  file.write('consumerKey=%s\n' % consumer_key)
  file.write('accessTokenSecret=%s\n' % token_secret)
  file.close()


def fetch(url):
  logging.debug('Now fetching: %s' % url)
  
  path = os.path.expanduser('~/.oacurl.properties')
  if not os.path.exists(path):
    logging.debug('User is not logged in.')
    
    print 'You are not logged in'
    sys.exit(1)

  properties = load_properties_file(path)
  oauth_parameters = {
    'consumer_key': properties['consumerKey'], 
    'consumer_secret' : properties['consumerSecret'],
    'oauth_token' : properties['accessToken'],
    'oauth_token_secret':properties['accessTokenSecret']}
  
  http = oauth_wrap.get_authorised_http(oauth_parameters)
  response, content = http.request(url)
  logging.debug(response)
  logging.debug(content)
  
  return response,content


def buzz_login():
  buzz_discovery = build("buzz", "v1").auth_discovery()

  flow = FlowThreeLegged(buzz_discovery,
                         consumer_key='anonymous',
                         consumer_secret='anonymous',
                         user_agent='google-api-client-python-buzz-cmdline/1.0',
                         domain='anonymous',
                         scope='https://www.googleapis.com/auth/buzz',
                         xoauth_displayname='oacurl.py')

  authorize_url = flow.step1_get_authorize_url()

  print 'Go to the following link in your browser:'
  print authorize_url
  print

  accepted = 'n'
  while accepted.lower() == 'n':
      accepted = raw_input('Have you authorized me? (y/n) ')
  verification = raw_input('What is the verification code? ').strip()

  credentials = flow.step2_exchange(verification)
  path = os.path.expanduser('~/.oacurl.properties')
  save_properties('anonymous', 'anonymous', credentials.token.key, credentials.token.secret,path)
  
  
def generic_login():
  #TODO(ade) Implement support for other services
  print 'Support for services other than Buzz is not implemented yet. Sorry.'


def login(options):
  if options.buzz:
    buzz_login()
  else:
    generic_login()


def get_command(args):
  if args and args[0] == 'login':
    return 'login'
  if args and args[0] == 'fetch':
    return 'fetch'
  return None


def configure_logging(options):
  if options.verbose:
    logging.basicConfig(level=logging.DEBUG)


def main():
  usage = '''Usage: python %prog [options] fetch <url>
  Example: python %prog -v fetch "https://www.googleapis.com/buzz/v1/people/@me/@self?alt=json&pp=1"
  '''
  parser = optparse.OptionParser(usage=usage)
  parser.set_defaults(verbose=False)
  parser.add_option('-v', '--verbose', action='store_true', dest='verbose')
  parser.add_option('-q', '--quiet', action='store_false', dest='verbose')
  parser.add_option('--buzz', action='store_true', dest='buzz')
  
  (options, args) = parser.parse_args()

  configure_logging(options)
  logging.debug('Options: %s and Args: %s' % (str(options), str(args)))
  
  command = get_command(args)
  
  if not command:
    parser.error('Invalid arguments')
    return
  
  if command == 'fetch':
    response, content = fetch(args[1])
    print response
    print content
    return
  
  if command == 'login':
    login(options)

if __name__ == '__main__':
  main()