#!/bin/bash
#
# Copyright 2014 Google Inc. All Rights Reserved.
# Author: jcgregorio@google.com (Joe Gregorio)
#
# Uploads a training data set to Google Storage to be used by this sample
# application.
#
# Usage:
# setup.sh file_name bucket/object
#
# Requirements:
#   gsutil - a client application for interacting with Google Storage. It
#     can be downloaded from https://code.google.com/apis/storage/docs/gsutil.html
FILE_NAME=$1
OBJECT_NAME=$2
gsutil cp $FILE_NAME gs://$OBJECT_NAME
