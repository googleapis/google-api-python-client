# Copyright 2023 Google Inc. All rights reserved.
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

"""Unit tests for describe"""

import unittest
from googleapiclient import describe


# run this test file using nox -s "unit-3.8(oauth2client=None)" -- -k test_describe.py

class TestDescribe(unittest.TestCase):
    def test_safe_version_basic(self):
        self.assertEqual(describe.safe_version("testingv1.3"), "testingv1_3")

    def test_safe_version_already_updated(self):
        self.assertEqual(describe.safe_version("testingv1_3"), "testingv1_3")

    def test_safe_version_empty(self):
        self.assertEqual(describe.safe_version(""), "")

    def test_safe_version_fail(self):
        with self.assertRaises(Exception) as context:
            describe.safe_version(16)
        # TODO confirm the exception issomething that we expect

    def test_unsafe_version_basic(self):
        self.assertEqual(describe.unsafe_version("testingv1_3"), "testingv1.3")
    
    def test_unsafe_version_already_updated(self):
        self.assertEqual(describe.unsafe_version("testingv1.3"), "testingv1.3")
    
    def test_unsafe_version_empty(self):
        self.assertEqual(describe.unsafe_version(""), "")

    def test_unsafe_version_fail(self):
        with self.assertRaises(Exception) as context:
            describe.unsafe_version(16)
        # TODO confirm the exception issomething that we expect

    @unittest.skip("skipping until this is implemented")
    def test_method_params(self):
        # TODO
        print("TODO")

    @unittest.skip("skipping until this is implemented")
    def test_method(self):
        # TODO
        print("TODO")
    
    def test_breadcrumbs_basic(self):
        self.assertEqual(describe.breadcrumbs(
            "resource1.resource2.resource3", #resources (path)
            {"title": "Document Title"} ), #root_discovery document
            #returned string
            '<a href="resource1.html">Document Title</a> . <a href="resource1.resource2.html">resource2</a> . <a href="resource1.resource2.resource3.html">resource3</a>')
        
    def test_breadcrumbs_no_title(self):
        self.assertEqual(describe.breadcrumbs(
            "resource1.resource2.resource3", #resources (path)
            {"not title": "Title"} ), #root_discovery document
            #returned string
            '<a href="resource1.html">resource1</a> . <a href="resource1.resource2.html">resource2</a> . <a href="resource1.resource2.resource3.html">resource3</a>')

    def test_breadcrumbs_empty_root_discovery(self):
        self.assertEqual(describe.breadcrumbs(
            "resource1.resource2.resource3", #resources (path)
            {} ), #root_discovery document
            #returned string
            '<a href="resource1.html">resource1</a> . <a href="resource1.resource2.html">resource2</a> . <a href="resource1.resource2.resource3.html">resource3</a>')
        
    def test_breadcrumbs_empty_path(self):
        self.assertEqual(describe.breadcrumbs(
            "", #resources (path)
            {"title": "Title"} ), #root_discovery document
            #returned string
            '<a href=".html">Title</a>')

    @unittest.skip("skipping until this is implemented")
    def test_document_collection(self):
        # TODO
        print("TODO")

    @unittest.skip("skipping until this is implemented")
    def test_document_collection_recursive(self):
        # TODO
        print("TODO")
    
    @unittest.skip("skipping until this is implemented")
    def test_document_api(self):
        # TODO
        print("TODO")

    @unittest.skip("skipping until this is implemented")
    def test_document_api_from_discovery_document( self):
        # TODO implement me to have the program work from top to bottom
        discovery_url = ""
        doc_destination_dir = ""
        artifact_destination_dir = ""
        describe.document_api_from_discovery_document(discovery_url, doc_destination_dir, artifact_destination_dir)

    @unittest.skip("skipping until this is implemented")
    def test_generate_all_api_documents(self):
        # TODO
        print("TODO")
    


    

if __name__ == "__main__":
    unittest.main()
