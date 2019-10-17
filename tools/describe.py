#!/usr/bin/python
#
# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Create documentation for generate API surfaces.

Command-line tool that creates documentation for all APIs listed in discovery.
The documentation is generated from a combination of the discovery document and
the generated API surface itself.
"""

__author__ = "jcgregorio@google.com (Joe Gregorio)"

from collections import OrderedDict
import argparse
import collections
import json
import os
import re
import string
import sys

import requests

from googleapiclient.discovery import DISCOVERY_URI
from googleapiclient.discovery import build
from googleapiclient.discovery import build_from_document
from googleapiclient.discovery import UnknownApiNameOrVersion
import uritemplate

CSS = """<style>

    body, h1, h2, h3, div, span, p, pre, a {
      margin: 0;
      padding: 0;
      border: 0;
      font-weight: inherit;
      font-style: inherit;
      font-size: 100%;
      font-family: inherit;
      vertical-align: baseline;
    }
    
    body {
      font-size: 13px;
      padding: 1em;
    }
    
    h1 {
      font-size: 26px;
      margin-bottom: 1em;
    }
    
    h2 {
      font-size: 24px;
      margin-bottom: 1em;
    }
    
    h3 {
      font-size: 20px;
      margin-bottom: 1em;
      margin-top: 1em;
    }
    
    pre, code {
      line-height: 1.5;
      font-family: Monaco, 'DejaVu Sans Mono', 'Bitstream Vera Sans Mono', 'Lucida Console', monospace;
    }
    
    pre {
      margin-top: 0.5em;
    }
    
    h1, h2, h3, p {
      font-family: Arial, sans serif;
    }
    
    h1, h2, h3 {
      border-bottom: solid #CCC 1px;
    }
    
    .toc_element {
      margin-top: 0.5em;
    }
    
    .firstline {
      margin-left: 2 em;
    }
    
    .method  {
      margin-top: 1em;
      border: solid 1px #CCC;
      padding: 1em;
      background: #EEE;
    }
    
    .details {
      font-weight: bold;
      font-size: 14px;
    }
    
    </style>"""

METHOD_TEMPLATE = """<div class="method">
    <code class="details" id="$name">$name($params)</code>
  <pre>$doc</pre>
</div>
"""

COLLECTION_LINK = """<p class="toc_element">
  <code><a href="$href">$name()</a></code>
</p>
<p class="firstline">Returns the $name Resource.</p>
"""

METHOD_LINK = """<p class="toc_element">
  <code><a href="#$name">$name($params)</a></code></p>
<p class="firstline">$firstline</p>"""

BASE = "docs/dyn"

DIRECTORY_URI = "https://www.googleapis.com/discovery/v1/apis"

parser = argparse.ArgumentParser(description=__doc__)

parser.add_argument(
    "--discovery_uri_template",
    default=DISCOVERY_URI,
    help="URI Template for discovery.",
)

parser.add_argument(
    "--discovery_uri",
    default="",
    help=(
        "URI of discovery document. If supplied then only "
        "this API will be documented."
    ),
)

parser.add_argument(
    "--directory_uri",
    default=DIRECTORY_URI,
    help=("URI of directory document. Unused if --discovery_uri" " is supplied."),
)

parser.add_argument(
    "--dest", default=BASE, help="Directory name to write documents into."
)


def safe_version(version):
    """
    Create a safe version of the version string.

    Needed so that we can distinguish between versions
    and sub-collections in URIs. I.e. we don't want
    adsense_v1.1 to refer to the '1' collection in the v1
    version of the adsense api.

    Args:
        version (str): The version string.
    Returns:
        The string with '.' replaced with '_'.
    """

    return version.replace(".", "_")


def unsafe_version(version):
    """
    Undoes what safe_version() does.

    See safe_version() for the details.


    Args:
        version (str): The safe version string.
    Returns:
        The string with '_' replaced with '.'.
    """

    return version.replace("_", ".")


def method_params(doc):
    """
    Document the parameters of a method.

    Args:
        doc (string): The method's docstring.

    Returns:
        str: the method signature.
    """
    doclines = doc.splitlines()
    if "Args:" in doclines:
        begin = doclines.index("Args:")
        if "Returns:" in doclines[begin + 1 :]:
            end = doclines.index("Returns:", begin)
            args = doclines[begin + 1 : end]
        else:
            args = doclines[begin + 1 :]

        parameters = []
        pname = None
        desc = ""

        def add_param(pname, desc):
            if pname is None:
                return
            if "(required)" not in desc:
                pname = pname + "=None"
            parameters.append(pname)

        for line in args:
            m = re.search("^\s+([a-zA-Z0-9_]+): (.*)", line)
            if m is None:
                desc += line
                continue
            add_param(pname, desc)
            pname = m.group(1)
            desc = m.group(2)
        add_param(pname, desc)
        parameters = ", ".join(parameters)
    else:
        parameters = ""
    return parameters


def method(name, doc):
    """
    Documents an individual method.

    Args:
        name (str): Name of the method.
        doc (str): The method's docstring.
    
    Returns:
        str: documentation for a method
    """

    params = method_params(doc)
    return string.Template(METHOD_TEMPLATE).substitute(
        name=name, params=params, doc=doc
    )


def breadcrumbs(path, root_discovery):
    """
    Create the breadcrumb trail to this page of documentation.

    Args:
        path (str): Dot separated name of the resource.
        root_discovery (dict): Deserialized discovery document.

    Returns:
        str: HTML with links to each of the parent resources of this resource.
    """
    parts = path.split(".")

    crumbs = []
    accumulated = []

    for i, p in enumerate(parts):
        prefix = ".".join(accumulated)
        # The first time through prefix will be [], so we avoid adding in a
        # superfluous '.' to prefix.
        if prefix:
            prefix += "."
        display = p
        if i == 0:
            display = root_discovery.get("title", display)
        crumbs.append('<a href="%s.html">%s</a>' % (prefix + p, display))
        accumulated.append(p)

    return " . ".join(crumbs)


def document_collection(resource, path, root_discovery, discovery, css=CSS):
    """
    Document a single collection in an API.

    Args:
        resource: Collection or service being documented.
        path (str): Dot separated name of the resource.
        root_discovery (dict): Deserialized discovery document.
        discovery (dict): Deserialized discovery document, but just the portion that
          describes the resource.
        css (str): The CSS to include in the generated file.
    
    Returns:
        str: html for a single collection
    """
    collections = []
    methods = []
    resource_name = path.split(".")[-2]
    html = [
        "<html><body>",
        css,
        "<h1>%s</h1>" % breadcrumbs(path[:-1], root_discovery),
        "<h2>Instance Methods</h2>",
    ]

    # Which methods are for collections.
    for name in dir(resource):
        if not name.startswith("_") and callable(getattr(resource, name)):
            if hasattr(getattr(resource, name), "__is_resource__"):
                collections.append(name)
            else:
                methods.append(name)

    # TOC
    if collections:
        for name in collections:
            if not name.startswith("_") and callable(getattr(resource, name)):
                href = path + name + ".html"
                html.append(
                    string.Template(COLLECTION_LINK).substitute(href=href, name=name)
                )

    if methods:
        for name in methods:
            if not name.startswith("_") and callable(getattr(resource, name)):
                doc = getattr(resource, name).__doc__
                params = method_params(doc)
                firstline = doc.splitlines()[0]
                html.append(
                    string.Template(METHOD_LINK).substitute(
                        name=name, params=params, firstline=firstline
                    )
                )

    if methods:
        html.append("<h3>Method Details</h3>")
        for name in methods:
            dname = name.rsplit("_")[0]
            html.append(method(name, getattr(resource, name).__doc__))

    html.append("</body></html>")

    return "\n".join(html)


def document_collection_recursive(resource, path, root_discovery, discovery, dest):
    html = document_collection(resource, path, root_discovery, discovery)

    with open(os.path.join(dest, path + "html"), "w") as f:
        f.write(html)

    for name in dir(resource):
        if (
            not name.startswith("_")
            and callable(getattr(resource, name))
            and hasattr(getattr(resource, name), "__is_resource__")
            and discovery != {}
        ):
            dname = name.rsplit("_")[0]
            try:
                collection = getattr(resource, name)()
            except KeyError as e:
                print(f"Warning: {path} has an invalid collection for {name}")
            document_collection_recursive(
                collection,
                path + name + ".",
                root_discovery,
                discovery["resources"].get(dname, {}),
                dest,
            )


def document_api(name, version, dest, uri_template=DISCOVERY_URI):
    """
    Document the given API.

    Args:
        name (str): Name of the API.
        version (str): Version of the API.
    """
    try:
        service = build(name, version)
    except UnknownApiNameOrVersion as e:
        print(f"Warning: {name} {version} found but could not be built.")
        return

    response = requests.get(
        uritemplate.expand(uri_template, {"api": name, "apiVersion": version})
    )
    try:
        discovery = response.json()
        version = safe_version(version)
        document_collection_recursive(
            service, f"{name}_{version}.", discovery, discovery, dest
        )
    except json.decoder.JSONDecodeError:
        print(
            f"Warning: {name} {version} found but could not be built due to invalid JSON"
        )


def document_api_from_discovery_document(uri, dest):
    """
    Document the given API from a discovery document.

    Args:
        uri (str): URI of discovery document.
    """
    response = requests.get(uri)
    response.raise_for_status()
    discovery = response.json()

    service = build_from_document(discovery)

    name = discovery["version"]
    version = safe_version(discovery["version"])

    document_collection_recursive(
        service, f"{name}_{version}.", discovery, discovery, dest
    )


def document_all_apis(*, base_path=BASE):
    """
    Generate docs for all the APIs listed in the directory uri.
    """

    api_directory = collections.defaultdict(list)
    response = requests.get(DIRECTORY_URI)
    if response.status_code == 200:
        directory = response.json()["items"]
        for api in directory:
            document_api(api["name"], api["version"], base_path)
            api_directory[api["name"]].append(safe_version(api["version"]))

        # sort by api name and version number
        for api in api_directory:
            api_directory[api] = sorted(api_directory[api])
        api_directory = OrderedDict(sorted(api_directory.items(), key=lambda x: x[0]))

        markdown = []
        for api, versions in api_directory.items():
            markdown.append(f"## {api}")
            for version in versions:
                markdown.append(f"* [{version}]({base_path}/{api}_{version}.html)")
            markdown.append("\n")

        with open(f"{base_path}/index.md", "w") as f:
            f.write("\n".join(markdown))

    else:
        response.raise_for_status()


if __name__ == "__main__":
    FLAGS = parser.parse_args(sys.argv[1:])

    if FLAGS.discovery_uri:
        document_api_from_discovery_document(FLAGS.discovery_uri, dest=FLAGS.dest)
    else:
        document_all_apis(base_path=FLAGS.dest)
