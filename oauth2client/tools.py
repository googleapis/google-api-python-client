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

"""Command-line tools for authenticating via OAuth 2.0

Do the OAuth 2.0 Web Server dance for a command line application. Stores the
generated credentials in a common file that is used by other example apps in
the same directory.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'
__all__ = ['run']


def run(flow, storage):
  """Core code for a command-line application.

  Args:
    flow: Flow, an OAuth 2.0 Flow to step through.
    storage: Storage, a Storage to store the credential in.

  Returns:
    Credentials, the obtained credential.

  Exceptions:
    RequestError: if step2 of the flow fails.
  """
  authorize_url = flow.step1_get_authorize_url('oob')

  print 'Go to the following link in your browser:'
  print authorize_url
  print

  accepted = 'n'
  while accepted.lower() == 'n':
    accepted = raw_input('Have you authorized me? (y/n) ')
  code = raw_input('What is the verification code? ').strip()

  try:
    credentials = flow.step2_exchange(code)
  except RequestError:
    sys.exit('The authentication has failed.')

  storage.put(credentials)
  credentials.set_store(storage.put)

  print 'You have successfully authenticated.'

  return credentials
