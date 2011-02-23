#!/usr/bin/python2.4
#
# -*- coding: utf-8 -*-
#
# Copyright 2011 Google Inc. All Rights Reserved.

"""Simple command-line example for Google Prediction API.

Command-line application that trains on some data. This
sample does the same thing as the Hello Prediction! example.

  http://code.google.com/apis/predict/docs/hello_world.html
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import httplib2
import pprint
import time

from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage
from oauth2client.tools import run

# Uncomment to get low level HTTP logging
#httplib2.debuglevel = 4

# Name of Google Storage bucket/object that contains the training data
OBJECT_NAME = "apiclient-prediction-sample/prediction_models/languages"


def main():
  storage = Storage('prediction.dat')
  credentials = storage.get()

  if credentials is None or credentials.invalid == True:
    flow = OAuth2WebServerFlow(
        # You MUST put in your client id and secret here for this sample to
        # work. Visit https://code.google.com/apis/console to get your client
        # credentials.
        client_id='<Put Your Client ID Here>',
        client_secret='<Put Your Client Secret Here>',
        scope='https://www.googleapis.com/auth/prediction',
        user_agent='prediction-cmdline-sample/1.0',
        xoauth_displayname='Prediction Example App')

    credentials = run(flow, storage)

  http = httplib2.Http()
  http = credentials.authorize(http)

  service = build("prediction", "v1.1", http=http)

  # Start training on a data set
  train = service.training()
  start = train.insert(data=OBJECT_NAME, body={}).execute()

  print 'Started training'
  pprint.pprint(start)

  # Wait for the training to complete
  while 1:
    status = train.get(data=OBJECT_NAME).execute()
    pprint.pprint(status)
    if 'accuracy' in status['modelinfo']:
      break
    print 'Waiting for training to complete.'
    time.sleep(10)
  print 'Training is complete'

  # Now make a prediction using that training
  body = {'input': {'mixture':["mucho bueno"]}}
  prediction = service.predict(body=body, data=OBJECT_NAME).execute()
  print 'The prediction is:'
  pprint.pprint(prediction)

if __name__ == '__main__':
  main()
