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

"""Do the OAuth 2.0 Web Server dance.

Do the OAuth 2.0 Web Server dance for
a command line application. Store the generated
credentials in a common file that is used by
other example apps in the same directory.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run

flow = OAuth2WebServerFlow(
    client_id='433807057907.apps.googleusercontent.com',
    client_secret='jigtZpMApkRxncxikFpR+SFg',
    scope='https://www.googleapis.com/auth/moderator',
    user_agent='moderator-cmdline-sample/1.0',
    xoauth_displayname='Moderator Client Example App')

run(flow, 'moderator.dat')
