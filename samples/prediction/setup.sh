#!/bin/bash
#
# Copyright 2011 Google Inc. All Rights Reserved.
# Author: jcgregorio@google.com (Joe Gregorio)
#
# Uploads a training data set to Google Storage to be used by this sample
# application. 
#
# Usage:
# setup.sh bucket/object 
#
# Requirements:
#   gsutil - a client application for interacting with Google Storage. It
#     can be downloaded from https://code.google.com/apis/storage/docs/gsutil.html
OBJECT_NAME=$1
gsutil cp language_id.txt gs://$OBJECT_NAME
