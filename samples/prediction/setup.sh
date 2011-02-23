#!/bin/bash
#
# Copyright 2011 Google Inc. All Rights Reserved.
# Author: jcgregorio@google.com (Joe Gregorio)
#
# Uploads a training data set to Google Storage to be used by this sample
# application. Download the 'language.txt' file from
# http://code.google.com/apis/predict/docs/hello_world.html
#
# Requirements:
#   gsutil - a client application for interacting with Google Storage. It
#     can be downloaded from https://code.google.com/apis/storage/docs/gsutil.html
gsutil cp ./language_id.txt gs://apiclient-prediction-sample/prediction_models/languages
