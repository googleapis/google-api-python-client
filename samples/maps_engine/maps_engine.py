# -*- coding: utf-8 -*-
#
#  Copyright 2013 Google Inc. All Rights Reserved.
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

"""Simple command-line sample for Google Maps Engine.

This sample code demonstrates use of Google Maps Engine. These samples do not
make use of the Discovery Service, but do use the the httplib2 library to make
authenticated requests.  For more information on Google Maps Engine, see
developers.google.com/maps-engine/documentation/

These samples allow you to
1) List projects you have access to, or
2) List tables in a given project, and upload a shapefile.

Usage:
  $ python maps_engine.py [-p project_id] [-s shapefile]

If you do not enter a shapefile, it will upload the included "polygons".

You can also get help on all the command-line flags the program understands
by running:

  $ python maps_engine.py --help

To get detailed log output run:

  $ python maps_engine.py -p 123456 --logging_level=DEBUG
"""

__author__ = "jlivni@google.com (Josh Livni)"

import argparse
import json
import logging
import sys
import time

import sample_tools

logging.basicConfig(level=logging.INFO)

# Declare command-line flags.
argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument("-p", "--project_id", help="optional GME Project ID")
argparser.add_argument("-s", "--shapefile", help="Shapefile (without the .shp)")

BASE_URL = "https://www.googleapis.com/mapsengine/v1/tables/"
SUCCESSFUL_STATUS = ["processed", "complete", "ready"]

class MapsEngineSampleException(Exception):
  """Catch this for failures specific to this sample code."""


def ListProjects(http):
  """List the projects available to the authorized account.

  Args:
    http: http, authorized http object.
  """

  url = "https://www.googleapis.com/mapsengine/v1/projects"
  resp, content = http.request(url, method="GET")
  RaiseBadResponse(resp, url)
  logging.info(content)


def ListTables(http, project_id):
  """List the tables in a given project.

  Args:
    http: http, authenticated http object.
    project_id: string, id of the GME project.
  """
  table_url = "https://www.googleapis.com/mapsengine/v1/tables?projectId=%s"
  url = table_url % project_id
  resp, content = http.request(url, method="GET")
  RaiseBadResponse(resp, url)
  logging.info(content)


def UploadShapefile(http, project_id, shapefile_prefix):
  """Upload a shapefile to a given project, and display status when complete.

  Args:
    http: http, authenticated http object.
    project_id: string, id of the GME project.
    shapefile_prefix: string, the shapefile without the .shp suffix.
  """
  # Note the different endpoint for uploading the actual data.
  upload_url = "https://www.googleapis.com/upload/mapsengine/v1/tables/"

  # Ensure json encoding for POST
  headers = {"Content-Type": "application/json"}

  # Upload a file containing info about your upload
  suffixes = ["shp", "dbf", "prj", "shx"]
  files = []
  for suffix in suffixes:
    files.append({
        "filename": "%s.%s" % (shapefile_prefix, suffix)
    })
  metadata = {
      "projectId": project_id,
      "name": shapefile_prefix,
      "description": "polygons that were uploaded by a script",
      "files": files,
      # You need the string value of a valid shared and published ACL
      # Check the "Access Lists" section of the Maps Engine UI for a list.
      "draftAccessList": "Map Editors",
      "tags": [shapefile_prefix, "auto_upload", "kittens"]
  }

  body = json.dumps(metadata)
  create_url = "".join([BASE_URL, "upload"])

  logging.info("Uploading metadata for %s", shapefile_prefix)

  resp, content = http.request(create_url,
                               method="POST",
                               headers=headers,
                               body=body)
  RaiseBadResponse(resp, create_url)
  logging.debug(content)

  # We have now created an empty asset. Get Table ID to upload the actual files.
  result = json.loads(content)
  table_id = result["id"]

  # A shapefile is actually a bunch of files; GME requires these for suffixes.
  for suffix in suffixes:
    shapefile = "%s.%s" % (shapefile_prefix, suffix)
    url = "%s%s/files?filename=%s" % (upload_url, table_id, shapefile)
    logging.debug("upload url is %s", url)

    with open(shapefile, "rb") as opened:
      headers = {
          "Content-Type": "application/octet-stream"
      }

      logging.info("Uploading %s", shapefile)
      resp, content = http.request(url,
                                   method="POST",
                                   headers=headers,
                                   body=opened)
      RaiseBadResponse(resp, url)
      logging.debug(content)

  # Check everything completed.
  CheckTableStatus(http, table_id)


def CheckTableStatus(http, table_id):
  url = BASE_URL + table_id
  resp, content = http.request(url)
  RaiseBadResponse(resp, url)
  status = json.loads(content)["processingStatus"]
  logging.info("Table Status: %s", status)
  if status in SUCCESSFUL_STATUS:
    logging.info("table successfully processed; the table id is %s\n", table_id)
    cid = table_id.split("_")[0]
    gme_url = "https://earthbuilder.google.com/admin/#RepositoryPlace:"
    gme_url += "cid=%s&v=DETAIL_INFO&aid=%s" % (cid, table_id)
    logging.info("See it at %s", gme_url)
  else:
    logging.info("Table %s; will check again in 5 seconds", status)
    time.sleep(5)
    CheckTableStatus(http, table_id)


def RaiseBadResponse(response, url):
  """Tests GME API returned a valid 2xx response.

  Args:
    response: the JSON response from the API.
    url: the original request URL.
  Raises:
    MapsEngineSampleException: Custom exception in case of non 2xx response.
  """
  if not response["status"].startswith("2"):
    raise MapsEngineSampleException("request failed: %s", url)


def main(argv):
  http, flags = sample_tools.init(
      argv, "mapsengine", "v1", __doc__, __file__, parents=[argparser],
      scope="https://www.googleapis.com/auth/mapsengine")

  if flags.project_id:
    ListTables(http, flags.project_id)
    UploadShapefile(http, flags.project_id, flags.shapefile or "polygons")
  else:
    ListProjects(http)
  return


if __name__ == "__main__":
  main(sys.argv)
