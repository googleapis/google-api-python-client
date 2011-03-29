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
"""Sample for threading and queues.

A simple sample that processes many requests by constructing a threadpool and
passing client requests by a thread queue to be processed.
"""
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run

import Queue
import gflags
import httplib2
import logging
import sys
import threading
import time

# How many threads to start.
NUM_THREADS = 3

# A list of URLs to shorten.
BULK = [
    "https://code.google.com/apis/buzz/",
    "https://code.google.com/apis/moderator/",
    "https://code.google.com/apis/latitude/",
    "https://code.google.com/apis/urlshortener/",
    "https://code.google.com/apis/customsearch/",
    "https://code.google.com/apis/shopping/search/",
    "https://code.google.com/apis/predict",
    "https://code.google.com/more",
    ]

FLAGS = gflags.FLAGS
FLOW = OAuth2WebServerFlow(
    client_id='433807057907.apps.googleusercontent.com',
    client_secret='jigtZpMApkRxncxikFpR+SFg',
    scope='https://www.googleapis.com/auth/urlshortener',
    user_agent='urlshortener-cmdline-sample/1.0')

gflags.DEFINE_enum('logging_level', 'ERROR',
    ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    'Set the level of logging detail.')

queue = Queue.Queue()


class Backoff:
  """Exponential Backoff

  Implements an exponential backoff algorithm.
  Instantiate and call loop() each time through
  the loop, and each time a request fails call
  fail() which will delay an appropriate amount
  of time.
  """

  def __init__(self, maxretries=8):
    self.retry = 0
    self.maxretries = maxretries
    self.first = True

  def loop(self):
    if self.first:
      self.first = False
      return True
    else:
      return self.retry < self.maxretries

  def fail(self):
    self.retry += 1
    delay = 2 ** self.retry
    time.sleep(delay)


def start_threads(credentials):
  """Create the thread pool to process the requests."""

  def process_requests(n):
    http = httplib2.Http()
    http = credentials.authorize(http)
    loop = True


    while loop:
      request = queue.get()
      backoff = Backoff()
      while backoff.loop():
        try:
          response = request.execute(http)
          print "Processed: %s in thread %d" % (response['id'], n)
          break
        except HttpError, e:
          if e.resp.status in [402, 403, 408, 503, 504]:
            print "Increasing backoff, got status code: %d" % e.resp.status
            backoff.fail()
        except Exception, e:
          print "Unexpected error. Exiting." + str(e)
          loop = False
          break

      print "Completed request"
      queue.task_done()


  for i in range(NUM_THREADS):
    t = threading.Thread(target=process_requests, args=[i])
    t.daemon = True
    t.start()


def main(argv):
  try:
    argv = FLAGS(argv)
  except gflags.FlagsError, e:
    print '%s\\nUsage: %s ARGS\\n%s' % (e, argv[0], FLAGS)
    sys.exit(1)

  logging.getLogger().setLevel(getattr(logging, FLAGS.logging_level))

  storage = Storage('threadqueue.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid == True:
    credentials = run(FLOW, storage)

  start_threads(credentials)

  http = httplib2.Http()
  http = credentials.authorize(http)

  service = build("urlshortener", "v1", http=http,
            developerKey="AIzaSyDRRpR3GS1F1_jKNNM9HCNd2wJQyPG3oN0")
  shortener = service.url()

  for url in BULK:
    body = {"longUrl": url }
    shorten_request = shortener.insert(body=body)
    print "Adding request to queue"
    queue.put(shorten_request)

  # Wait for all the requests to finish
  queue.join()


if __name__ == "__main__":
  main(sys.argv)
