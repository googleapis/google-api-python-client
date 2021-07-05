#!/bin/bash

# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START startup_script]
apt-get update
apt-get -y install imagemagick

# Use the metadata server to get the configuration specified during
# instance creation. Read more about metadata here:
# https://cloud.google.com/compute/docs/metadata#querying
IMAGE_URL=$(curl http://metadata/computeMetadata/v1/instance/attributes/url -H "Metadata-Flavor: Google")
TEXT=$(curl http://metadata/computeMetadata/v1/instance/attributes/text -H "Metadata-Flavor: Google")
CS_BUCKET=$(curl http://metadata/computeMetadata/v1/instance/attributes/bucket -H "Metadata-Flavor: Google")

mkdir image-output
cd image-output
wget $IMAGE_URL
convert * -pointsize 30 -fill white -stroke black -gravity center -annotate +10+40 "$TEXT" output.png

# Create a Google Cloud Storage bucket.
gsutil mb gs://$CS_BUCKET

# Store the image in the Google Cloud Storage bucket and allow all users
# to read it.
gsutil cp -a public-read output.png gs://$CS_BUCKET/output.png

# [END startup_script]
