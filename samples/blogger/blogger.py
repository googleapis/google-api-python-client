#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
#
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

"""Simple command-line sample for Blogger.

Command-line application that retrieves the users blogs and posts.

Usage:
  $ python blogger.py

You can also get help on all the command-line flags the program understands
by running:

  $ python blogger.py --help

To get detailed log output run:

  $ python blogger.py --logging_level=DEBUG
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import sys

from oauth2client import client
from apiclient import sample_tools


def main(argv):
  # Authenticate and construct service.
  service, flags = sample_tools.init(
      argv, 'plus', 'v1', __doc__, __file__,
      scope='https://www.googleapis.com/auth/blogger')

  service = build('blogger', 'v2', http=http)

  try:

      users = service.users()

      # Retrieve this user's profile information
      thisuser = users.get(userId='self').execute(http=http)
      print 'This user\'s display name is: %s' % thisuser['displayName']

      # Retrieve the list of Blogs this user has write privileges on
      thisusersblogs = users.blogs().list(userId='self').execute()
      for blog in thisusersblogs['items']:
        print 'The blog named \'%s\' is at: %s' % (blog['name'], blog['url'])

      posts = service.posts()

      # List the posts for each blog this user has
      for blog in thisusersblogs['items']:
        print 'The posts for %s:' % blog['name']
        request = posts.list(blogId=blog['id'])
        while request != None:
          posts_doc = request.execute(http=http)
          if 'items' in posts_doc and not (posts_doc['items'] is None):
            for post in posts_doc['items']:
              print '  %s (%s)' % (post['title'], post['url'])
          request = posts.list_next(request, posts_doc)

  except client.AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run'
      'the application to re-authorize')

if __name__ == '__main__':
  main(sys.argv)
