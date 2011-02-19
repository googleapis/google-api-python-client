from apiclient.discovery import build
from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.ext.authtools import run
from apiclient.ext.file import Storage
from apiclient.oauth import CredentialsInvalidError
from apiclient.oauth import FlowThreeLegged

import Queue
import httplib2
import threading
import time

# Uncomment to get detailed logging
# httplib2.debuglevel = 4


NUM_THREADS = 4
NUM_ITEMS = 40

queue = Queue.Queue()


class Backoff:
  """Exponential Backoff

  Implements an exponential backoff algorithm.
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
  # Start up NUM_THREADS to handle requests

  def process_requests():
    http = httplib2.Http()
    http = credentials.authorize(http)
    credentials_ok = True

    while credentials_ok:
      request = queue.get()
      backoff = Backoff()
      while backoff.loop():
        try:
          request.execute(http)
          break
        except HttpError, e:
          if e.resp.status in [402, 403, 408, 503, 504]:
            print "Increasing backoff, got status code: %d" % e.resp.status
            backoff.fail()
        except CredentialsInvalidError:
          print "Credentials no long valid. Exiting."
          credentials_ok = False
          break

      print "Completed request"
      queue.task_done()


  for i in range(NUM_THREADS):
    t = threading.Thread(target=process_requests)
    t.daemon = True
    t.start()


def main():
  storage = Storage('moderator.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid == True:
    moderator_discovery = build("moderator", "v1").auth_discovery()

    flow = FlowThreeLegged(moderator_discovery,
                           consumer_key='anonymous',
                           consumer_secret='anonymous',
                           user_agent='python-threading-sample/1.0',
                           domain='anonymous',
                           scope='https://www.googleapis.com/auth/moderator',
                           xoauth_displayname='Google API Client Example App')

    credentials = run(flow, storage)

  start_threads(credentials)

  http = httplib2.Http()
  http = credentials.authorize(http)

  p = build("moderator", "v1", http=http)

  series_body = {
      "data": {
          "description": "An example of bulk creating topics",
          "name": "Using threading and queues",
          "videoSubmissionAllowed": False
          }
      }
  try:
    series = p.series().insert(body=series_body).execute()
    print "Created a new series"

    for i in range(NUM_ITEMS):
      topic_body = {
          "data": {
            "description": "Sample Topic # %d" % i,
            "name": "Sample",
            "presenter": "me"
            }
          }
      topic_request = p.topics().insert(seriesId=series['id']['seriesId'],
                                        body=topic_body)
      print "Adding request to queue"
      queue.put(topic_request)
  except CredentialsInvalidError:
    print 'Your credentials are no longer valid.'
    print 'Please re-run this application to re-authorize.'


  queue.join()


if __name__ == "__main__":
  main()
