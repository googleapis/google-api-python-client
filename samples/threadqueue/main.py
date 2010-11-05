from apiclient.discovery import build
from apiclient.discovery import HttpError

import Queue
import httplib2
import pickle
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
    delay = 2**self.retry
    time.sleep(delay)


def start_threads(credentials):
  # Start up NUM_THREADS to handle requests

  def process_requests():
    http = httplib2.Http()
    http = credentials.authorize(http)

    while True:
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

      print "Completed request"
      queue.task_done()

  for i in range(NUM_THREADS):
    t = threading.Thread(target=process_requests)
    t.daemon = True
    t.start()

def main():

  f = open("moderator.dat", "r")
  credentials = pickle.loads(f.read())
  f.close()

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
    topic_request = p.topics().insert(seriesId=series['id']['seriesId'], body=topic_body)
    print "Adding request to queue"
    queue.put(topic_request)

  queue.join()


if __name__ == "__main__":
  main()
