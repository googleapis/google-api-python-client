#!/usr/bin/python
#
# Copyright 2013 Google Inc. All Rights Reserved.
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

"""Gets all payments available for the logged in user's default account.

Tags: payments.list
"""

__author__ = 'jalc@google.com (Jose Alcerreca)'

import sys

from apiclient import sample_tools
from oauth2client import client

def main(argv):
  # Authenticate and construct service.
  service, unused_flags = sample_tools.init(
      argv, 'adsense', 'v1.4', __doc__, __file__, parents=[],
      scope='https://www.googleapis.com/auth/adsense.readonly')
  try:
    # Retrieve payments list in pages and display data as we receive it.
    request = service.payments().list()
    if request is not None:
      result = request.execute()
      print result
      if 'items' in result:
        payments = result['items']
        for payment in payments:
          print ('Payment with id "%s" of %s %s and date %s was found. '
                 % (str(payment['id']),
                    payment['paymentAmountMicros'],
                    payment['paymentAmountCurrencyCode'],
                    payment.get('paymentDate', 'unknown')))
      else:
        print 'No payments found!'
  except client.AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run the '
           'application to re-authorize')

if __name__ == '__main__':
  main(sys.argv)
