#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Google Inc. All Rights Reserved.
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

"""Build wiki page with a list of all samples.

The information for the wiki page is built from data found in all the README
files in the samples. The format of the README file is:


   Description is everything up to the first blank line.

   api: plus  (Used to look up the long name in discovery).
   keywords: appengine (such as appengine, oauth2, cmdline)

   The rest of the file is ignored when it comes to building the index.
"""
from __future__ import print_function

import httplib2
import itertools
import json
import os
import re

BASE_HG_URI = "http://code.google.com/p/google-api-python-client/source/" "browse/#hg"

http = httplib2.Http(".cache")
r, c = http.request("https://www.googleapis.com/discovery/v1/apis")
if r.status != 200:
    raise ValueError("Received non-200 response when retrieving Discovery.")

# Dictionary mapping api names to their discovery description.
DIRECTORY = {}
for item in json.loads(c)["items"]:
    if item["preferred"]:
        DIRECTORY[item["name"]] = item

# A list of valid keywords. Should not be taken as complete, add to
# this list as needed.
KEYWORDS = {
    "appengine": "Google App Engine",
    "oauth2": "OAuth 2.0",
    "cmdline": "Command-line",
    "django": "Django",
    "threading": "Threading",
    "pagination": "Pagination",
    "media": "Media Upload and Download",
}


def get_lines(name, lines):
    """Return lines that begin with name.

  Lines are expected to look like:

     name: space separated values

  Args:
    name: string, parameter name.
    lines: iterable of string, lines in the file.

  Returns:
    List of values in the lines that match.
  """
    retval = []
    matches = itertools.ifilter(lambda x: x.startswith(name + ":"), lines)
    for line in matches:
        retval.extend(line[len(name) + 1 :].split())
    return retval


def wiki_escape(s):
    """Detect WikiSyntax (i.e. InterCaps, a.k.a. CamelCase) and escape it."""
    ret = []
    for word in s.split():
        if re.match(r"[A-Z]+[a-z]+[A-Z]", word):
            word = "!%s" % word
        ret.append(word)
    return " ".join(ret)


def context_from_sample(api, keywords, dirname, desc, uri):
    """Return info for expanding a sample into a template.

  Args:
    api: string, name of api.
    keywords: list of string, list of keywords for the given api.
    dirname: string, directory name of the sample.
    desc: string, long description of the sample.
    uri: string, uri of the sample code if provided in the README.

  Returns:
    A dictionary of values useful for template expansion.
  """
    if uri is None:
        uri = BASE_HG_URI + dirname.replace("/", "%2F")
    else:
        uri = "".join(uri)
    if api is None:
        return None
    else:
        entry = DIRECTORY[api]
        context = {
            "api": api,
            "version": entry["version"],
            "api_name": wiki_escape(entry.get("title", entry.get("description"))),
            "api_desc": wiki_escape(entry["description"]),
            "api_icon": entry["icons"]["x32"],
            "keywords": keywords,
            "dir": dirname,
            "uri": uri,
            "desc": wiki_escape(desc),
        }
        return context


def keyword_context_from_sample(keywords, dirname, desc, uri):
    """Return info for expanding a sample into a template.

  Sample may not be about a specific api.

  Args:
    keywords: list of string, list of keywords for the given api.
    dirname: string, directory name of the sample.
    desc: string, long description of the sample.
    uri: string, uri of the sample code if provided in the README.

  Returns:
    A dictionary of values useful for template expansion.
  """
    if uri is None:
        uri = BASE_HG_URI + dirname.replace("/", "%2F")
    else:
        uri = "".join(uri)
    context = {
        "keywords": keywords,
        "dir": dirname,
        "uri": uri,
        "desc": wiki_escape(desc),
    }
    return context


def scan_readme_files(dirname):
    """Scans all subdirs of dirname for README files.

  Args:
    dirname: string, name of directory to walk.

  Returns:
    (samples, keyword_set): list of information about all samples, the union
      of all keywords found.
  """
    samples = []
    keyword_set = set()

    for root, dirs, files in os.walk(dirname):
        if "README" in files:
            filename = os.path.join(root, "README")
            with open(filename, "r") as f:
                content = f.read()
                lines = content.splitlines()
                desc = " ".join(itertools.takewhile(lambda x: x, lines))
                api = get_lines("api", lines)
                keywords = get_lines("keywords", lines)
                uri = get_lines("uri", lines)
                if not uri:
                    uri = None

                for k in keywords:
                    if k not in KEYWORDS:
                        raise ValueError(
                            "%s is not a valid keyword in file %s" % (k, filename)
                        )
                keyword_set.update(keywords)
                if not api:
                    api = [None]
                samples.append((api[0], keywords, root[1:], desc, uri))

    samples.sort()

    return samples, keyword_set


def main():
    # Get all the information we need out of the README files in the samples.
    samples, keyword_set = scan_readme_files("./samples")

    # Now build a wiki page with all that information. Accumulate all the
    # information as string to be concatenated when were done.
    page = ['<wiki:toc max_depth="3" />\n= Samples By API =\n']

    # All the samples, grouped by API.
    current_api = None
    for api, keywords, dirname, desc, uri in samples:
        context = context_from_sample(api, keywords, dirname, desc, uri)
        if context is None:
            continue
        if current_api != api:
            page.append(
                """
=== %(api_icon)s %(api_name)s ===

%(api_desc)s

Documentation for the %(api_name)s in [https://google-api-client-libraries.appspot.com/documentation/%(api)s/%(version)s/python/latest/ PyDoc]

"""
                % context
            )
            current_api = api

        page.append("|| [%(uri)s %(dir)s] || %(desc)s ||\n" % context)

    # Now group the samples by keywords.
    for keyword, keyword_name in KEYWORDS.iteritems():
        if keyword not in keyword_set:
            continue
        page.append("\n= %s Samples =\n\n" % keyword_name)
        page.append("<table border=1 cellspacing=0 cellpadding=8px>\n")
        for _, keywords, dirname, desc, uri in samples:
            context = keyword_context_from_sample(keywords, dirname, desc, uri)
            if keyword not in keywords:
                continue
            page.append(
                """
<tr>
  <td>[%(uri)s %(dir)s] </td>
  <td> %(desc)s </td>
</tr>"""
                % context
            )
        page.append("</table>\n")

    print("".join(page))


if __name__ == "__main__":
    main()
