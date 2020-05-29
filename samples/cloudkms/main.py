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

"""Mutual TLS example for Cloud KMS.

This application returns the list of key rings in global location. First fill in
the project and adc_cert_key_folder value, then set the GOOGLE_API_USE_MTLS
environment variable to one of the following values based on your need:
(1) "Never": This means we always use regular api endpoint. Since this is the
default value, there is no need to explicitly set it.
(2) "Always": This means we always use the mutual TLS api endpoint.
(3) "Auto": This means we auto switch to mutual TLS api endpoint, if the ADC
client cert and key are detected.
"""
from __future__ import print_function
import google.api_core.client_options
import google.oauth2.credentials

from googleapiclient.discovery import build

project = "FILL IN YOUR PROJECT ID"

# The following are the file paths to save ADC client cert and key. If you don't
# want to use mutual TLS, simply ignore adc_cert_key_folder, and set adc_cert_path
# and adc_key_path to None.
adc_cert_key_folder = "FILL IN THE PATH WHERE YOU WANT TO SAVE ADC CERT AND KEY"
adc_cert_path = adc_cert_key_folder + "cert.pem"
adc_key_path = adc_cert_key_folder + "key.pem"


def main():
    cred = google.oauth2.credentials.UserAccessTokenCredentials()

    parent = "projects/{project}/locations/{location}".format(
        project=project, location="global"
    )

    # Build a service object for interacting with the API.
    service = build(
        "cloudkms",
        "v1",
        credentials=cred,
        adc_cert_path=adc_cert_path,
        adc_key_path=adc_key_path,
    )

    # Return the list of key rings in global location.
    return service.projects().locations().keyRings().list(parent=parent).execute()


if __name__ == "__main__":
    main()
