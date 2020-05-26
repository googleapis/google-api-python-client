#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2020 Google Inc. All Rights Reserved.
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

"""Simple command-line example for Translate.

Command-line application that translates some text.
"""
from __future__ import print_function
import google.api_core.client_options
import google.oauth2.credentials

from googleapiclient.discovery import build

# project="study-auth-265119"
project = "sijun-mtls-demo"
path = "/usr/local/google/home/sijunliu/wks/google-api-python-client/samples/kms/"
adc_cert_path = path + "cert.pem"
adc_key_path = path + "key.pem"


def main():
    cred = google.oauth2.credentials.UserAccessTokenCredentials()

    parent = "projects/{project}/locations/{location}".format(
        project=project, location="global"
    )

    # Build a service object for interacting with the API. Visit
    # the Google APIs Console <http://code.google.com/apis/console>
    # to get an API key for your own application.
    service = build(
        "cloudkms",
        "v1",
        credentials=cred,
        adc_cert_path=adc_cert_path,
        adc_key_path=adc_key_path,
    )
    print(service.projects().locations().keyRings().list(parent=parent).execute())


if __name__ == "__main__":
    main()
