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

"""Unit tests for googleapiclient.schema."""
from __future__ import absolute_import

__author__ = "jcgregorio@google.com (Joe Gregorio)"

import json
import os
import unittest2 as unittest

from googleapiclient.schema import Schemas


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def datafile(filename):
    return os.path.join(DATA_DIR, filename)


LOAD_FEED = """{
    "items": [
      {
        "longVal": 42,
        "kind": "zoo#loadValue",
        "enumVal": "A String",
        "anyVal": "", # Anything will do.
        "nullVal": None,
        "stringVal": "A String",
        "doubleVal": 3.14,
        "booleanVal": True or False, # True or False.
      },
    ],
    "kind": "zoo#loadFeed",
  }"""


class SchemasTest(unittest.TestCase):
    def setUp(self):
        f = open(datafile("zoo.json"))
        discovery = f.read()
        f.close()
        discovery = json.loads(discovery)
        self.sc = Schemas(discovery)

    def test_basic_formatting(self):
        self.assertEqual(
            sorted(LOAD_FEED.splitlines()),
            sorted(self.sc.prettyPrintByName("LoadFeed").splitlines()),
        )

    def test_empty_edge_case(self):
        self.assertTrue("Unknown type" in self.sc.prettyPrintSchema({}))

    def test_simple_object(self):
        self.assertEqual({}, eval(self.sc.prettyPrintSchema({"type": "object"})))

    def test_string(self):
        self.assertEqual(
            type(""), type(eval(self.sc.prettyPrintSchema({"type": "string"})))
        )

    def test_integer(self):
        self.assertEqual(
            type(20), type(eval(self.sc.prettyPrintSchema({"type": "integer"})))
        )

    def test_number(self):
        self.assertEqual(
            type(1.2), type(eval(self.sc.prettyPrintSchema({"type": "number"})))
        )

    def test_boolean(self):
        self.assertEqual(
            type(True), type(eval(self.sc.prettyPrintSchema({"type": "boolean"})))
        )

    def test_string_default(self):
        self.assertEqual(
            "foo", eval(self.sc.prettyPrintSchema({"type": "string", "default": "foo"}))
        )

    def test_integer_default(self):
        self.assertEqual(
            20, eval(self.sc.prettyPrintSchema({"type": "integer", "default": 20}))
        )

    def test_number_default(self):
        self.assertEqual(
            1.2, eval(self.sc.prettyPrintSchema({"type": "number", "default": 1.2}))
        )

    def test_boolean_default(self):
        self.assertEqual(
            False,
            eval(self.sc.prettyPrintSchema({"type": "boolean", "default": False})),
        )

    def test_null(self):
        self.assertEqual(None, eval(self.sc.prettyPrintSchema({"type": "null"})))

    def test_any(self):
        self.assertEqual("", eval(self.sc.prettyPrintSchema({"type": "any"})))

    def test_array(self):
        self.assertEqual(
            [{}],
            eval(
                self.sc.prettyPrintSchema(
                    {"type": "array", "items": {"type": "object"}}
                )
            ),
        )

    def test_nested_references(self):
        feed = {
            "items": [
                {
                    "photo": {
                        "hash": "A String",
                        "hashAlgorithm": "A String",
                        "filename": "A String",
                        "type": "A String",
                        "size": 42,
                    },
                    "kind": "zoo#animal",
                    "etag": "A String",
                    "name": "A String",
                }
            ],
            "kind": "zoo#animalFeed",
            "etag": "A String",
        }

        self.assertEqual(feed, eval(self.sc.prettyPrintByName("AnimalFeed")))

    def test_additional_properties(self):
        items = {
            "animals": {
                "a_key": {
                    "photo": {
                        "hash": "A String",
                        "hashAlgorithm": "A String",
                        "filename": "A String",
                        "type": "A String",
                        "size": 42,
                    },
                    "kind": "zoo#animal",
                    "etag": "A String",
                    "name": "A String",
                }
            },
            "kind": "zoo#animalMap",
            "etag": "A String",
        }

        self.assertEqual(items, eval(self.sc.prettyPrintByName("AnimalMap")))

    def test_unknown_name(self):
        self.assertRaises(KeyError, self.sc.prettyPrintByName, "UknownSchemaThing")


if __name__ == "__main__":
    unittest.main()
