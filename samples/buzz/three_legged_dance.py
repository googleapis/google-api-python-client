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

"""Do the OAuth 1.0a three legged dance.

Do the OAuth 1.0a three legged dance for
a Buzz command line application. Store the generated
credentials in a common file that is used by
other example apps in the same directory.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

from apiclient.discovery import build
from apiclient.oauth import FlowThreeLegged

import pickle

buzz_discovery = build("buzz", "v1").auth_discovery()

flow = FlowThreeLegged(buzz_discovery,
                       consumer_key='anonymous',
                       consumer_secret='anonymous',
                       user_agent='google-api-client-python-buzz-cmdline/1.0',
                       domain='anonymous',
                       scope='https://www.googleapis.com/auth/buzz',
                       xoauth_displayname='Google API Client Example App')

authorize_url = flow.step1_get_authorize_url()

print 'Go to the following link in your browser:'
print authorize_url
print

accepted = 'n'
while accepted.lower() == 'n':
    accepted = raw_input('Have you authorized me? (y/n) ')
verification = raw_input('What is the verification code? ').strip()

credentials = flow.step2_exchange(verification)

f = open('buzz.dat', 'w')
f.write(pickle.dumps(credentials))
f.close()
