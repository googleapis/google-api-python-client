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
from __future__ import print_function

__author__ = "jcgregorio@google.com (Joe Gregorio)"

import argparse
import collections
import json
import pathlib
import re
import string
import sys

from googleapiclient.discovery import DISCOVERY_URI
from googleapiclient.discovery import build
from googleapiclient.discovery import build_from_document
from googleapiclient.http import build_http

import uritemplate

DISCOVERY_DOC_DIR = (
    pathlib.Path(__file__).parent.resolve()
    / "googleapiclient"
    / "discovery_cache"
    / "documents"
)

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

</style>
"""

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

BASE = pathlib.Path(__file__).parent.resolve() / "docs" / "dyn"

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
    """Create a safe version of the verion string.

    Needed so that we can distinguish between versions
    and sub-collections in URIs. I.e. we don't want
    adsense_v1.1 to refer to the '1' collection in the v1
    version of the adsense api.

    Args:
      version: string, The version string.
    Returns:
      The string with '.' replaced with '_'.
    """

    return version.replace(".", "_")


def unsafe_version(version):
    """Undoes what safe_version() does.

    See safe_version() for the details.


    Args:
      version: string, The safe version string.
    Returns:
      The string with '_' replaced with '.'.
    """

    return version.replace("_", ".")


def method_params(doc):
    """Document the parameters of a method.

    Args:
      doc: string, The method's docstring.

    Returns:
      The method signature as a string.
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
        sorted_parameters = []
        pname = None
        desc = ""

        def add_param(pname, desc):
            if pname is None:
                return
            if "(required)" not in desc:
                pname = pname + "=None"
                parameters.append(pname)
            else:
                # required params should be put straight into sorted_parameters
                # to maintain order for positional args
                sorted_parameters.append(pname)

        for line in args:
            m = re.search(r"^\s+([a-zA-Z0-9_]+): (.*)", line)
            if m is None:
                desc += line
                continue
            add_param(pname, desc)
            pname = m.group(1)
            desc = m.group(2)
        add_param(pname, desc)
        sorted_parameters.extend(sorted(parameters))
        sorted_parameters = ", ".join(sorted_parameters)
    else:
        sorted_parameters = ""
    return sorted_parameters


def method(name, doc):
    """Documents an individual method.

    Args:
      name: string, Name of the method.
      doc: string, The methods docstring.
    """
    import html

    params = method_params(doc)
    doc = html.escape(doc)
    return string.Template(METHOD_TEMPLATE).substitute(
        name=name, params=params, doc=doc
    )


def breadcrumbs(path, root_discovery):
    """Create the breadcrumb trail to this page of documentation.

    Args:
      path: string, Dot separated name of the resource.
      root_discovery: Deserialized discovery document.

    Returns:
      HTML with links to each of the parent resources of this resource.
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
        crumbs.append('<a href="{}.html">{}</a>'.format(prefix + p, display))
        accumulated.append(p)

    return " . ".join(crumbs)


def document_collection(resource, path, root_discovery, discovery, css=CSS):
    """Document a single collection in an API.

    Args:
      resource: Collection or service being documented.
      path: string, Dot separated name of the resource.
      root_discovery: Deserialized discovery document.
      discovery: Deserialized discovery document, but just the portion that
        describes the resource.
      css: string, The CSS to include in the generated file.
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


def document_collection_recursive(
    resource, path, root_discovery, discovery, doc_destination_dir
):
    html = document_collection(resource, path, root_discovery, discovery)

    f = open(pathlib.Path(doc_destination_dir).joinpath(path + "html"), "w")

    f.write(html)
    f.close()

    for name in dir(resource):
        if (
            not name.startswith("_")
            and callable(getattr(resource, name))
            and hasattr(getattr(resource, name), "__is_resource__")
            and discovery != {}
        ):
            dname = name.rsplit("_")[0]
            collection = getattr(resource, name)()
            document_collection_recursive(
                collection,
                path + name + ".",
                root_discovery,
                discovery["resources"].get(dname, {}),
                doc_destination_dir,
            )


def document_api(name, version, uri, doc_destination_dir):
    """Document the given API.

    Args:
        name (str): Name of the API.
        version (str): Version of the API.
        uri (str): URI of the API's discovery document
        doc_destination_dir (str): relative path where the reference
            documentation should be saved.
    """
    http = build_http()
    resp, content = http.request(
        uri
        or uritemplate.expand(
            FLAGS.discovery_uri_template, {"api": name, "apiVersion": version}
        )
    )

    if resp.status == 200:
        discovery = json.loads(content)
        service = build_from_document(discovery)
        doc_name = "{}.{}.json".format(name, version)
        discovery_file_path = DISCOVERY_DOC_DIR / doc_name
        revision = None

        pathlib.Path(discovery_file_path).touch(exist_ok=True)

        # Write discovery artifact to disk if revision equal or newer
        with open(discovery_file_path, "r+") as f:
            try:
                json_data = json.load(f)
                revision = json_data["revision"]
            except json.JSONDecodeError:
                revision = None

            if revision is None or discovery["revision"] >= revision:
                # Reset position to the beginning
                f.seek(0)
                # Write the changes to disk
                json.dump(discovery, f, indent=2, sort_keys=True)
                # Truncate anything left as it's not needed
                f.truncate()

    elif resp.status == 404:
        print(
            "Warning: {} {} not found. HTTP Code: {}".format(name, version, resp.status)
        )
        return
    else:
        print(
            "Warning: {} {} could not be built. HTTP Code: {}".format(
                name, version, resp.status
            )
        )
        return

    document_collection_recursive(
        service,
        "{}_{}.".format(name, safe_version(version)),
        discovery,
        discovery,
        doc_destination_dir,
    )


def document_api_from_discovery_document(discovery_url, doc_destination_dir):
    """Document the given API.

    Args:
      discovery_url (str): URI of discovery document.
      doc_destination_dir (str): relative path where the reference
          documentation should be saved.
    """
    http = build_http()
    response, content = http.request(discovery_url)
    discovery = json.loads(content)

    service = build_from_document(discovery)

    name = discovery["version"]
    version = safe_version(discovery["version"])

    document_collection_recursive(
        service,
        "{}_{}.".format(name, version),
        discovery,
        discovery,
        doc_destination_dir,
    )


def generate_all_api_documents(directory_uri=DIRECTORY_URI, doc_destination_dir=BASE):
    """Retrieve discovery artifacts and fetch reference documentations
    for all apis listed in the public discovery directory.
    args:
        directory_uri (str): uri of the public discovery directory.
        doc_destination_dir (str): relative path where the reference
            documentation should be saved.
    """
    api_directory = collections.defaultdict(list)
    http = build_http()
    resp, content = http.request(directory_uri)
    if resp.status == 200:
        directory = json.loads(content)["items"]
        for api in directory:
            document_api(
                api["name"],
                api["version"],
                api["discoveryRestUrl"],
                doc_destination_dir,
            )
            api_directory[api["name"]].append(api["version"])

        # sort by api name and version number
        for api in api_directory:
            api_directory[api] = sorted(api_directory[api])
        api_directory = collections.OrderedDict(
            sorted(api_directory.items(), key=lambda x: x[0])
        )

        markdown = []
        for api, versions in api_directory.items():
            markdown.append("## %s" % api)
            for version in versions:
                markdown.append(
                    "* [%s](http://googleapis.github.io/google-api-python-client/docs/dyn/%s_%s.html)"
                    % (version, api, safe_version(version))
                )
            markdown.append("\n")

        with open(BASE / "index.md", "w") as f:
            markdown = "\n".join(markdown)
            f.write(markdown)

    else:
        sys.exit("Failed to load the discovery document.")


if __name__ == "__main__":
    FLAGS = parser.parse_args(sys.argv[1:])
    if FLAGS.discovery_uri:
        document_api_from_discovery_document(
            discovery_url=FLAGS.discovery_uri, doc_destination_dir=FLAGS.dest
        )
    else:
        generate_all_api_documents(
            directory_uri=FLAGS.directory_uri, doc_destination_dir=FLAGS.dest
        )
