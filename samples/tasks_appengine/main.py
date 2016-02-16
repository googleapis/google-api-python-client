# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import webapp2
from webapp2_extras import jinja2

from googleapiclient.discovery import build
from oauth2client.contrib.appengine import OAuth2Decorator

import settings

decorator = OAuth2Decorator(client_id=settings.CLIENT_ID,
                            client_secret=settings.CLIENT_SECRET,
                            scope=settings.SCOPE)
service = build('tasks', 'v1')


class MainHandler(webapp2.RequestHandler):

  def render_response(self, template, **context):
    renderer = jinja2.get_jinja2(app=self.app)
    rendered_value = renderer.render_template(template, **context)
    self.response.write(rendered_value)

  @decorator.oauth_aware
  def get(self):
    if decorator.has_credentials():
      result = service.tasks().list(tasklist='@default').execute(
          http=decorator.http())
      tasks = result.get('items', [])
      for task in tasks:
        task['title_short'] = truncate(task['title'], 26)
      self.render_response('index.html', tasks=tasks)
    else:
      url = decorator.authorize_url()
      self.render_response('index.html', tasks=[], authorize_url=url)


def truncate(s, l):
  return s[:l] + '...' if len(s) > l else s


application = webapp2.WSGIApplication([
    ('/', MainHandler),
    (decorator.callback_path, decorator.callback_handler()),
    ], debug=True)
