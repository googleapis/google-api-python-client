#!/usr/bin/env python3
#
# Copyright 2019 Google, Inc.
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


# [START cloudsupport_search_case_classifications]
import googleapiclient.discovery


def caseClassifications_search(query: str) -> None:
    """
    Searches for case classifications using the Cloud Support API.

    Before running, please purchase a Cloud Customer Care service (https://cloud.google.com/support)
    and follow the Cloud Support API's getting started guide (https://cloud.google.com/support/docs/reference/v2#getting-started).

    Args:
        query: The query to use to filter the search.
               Example: 'display_name:"*Compute Engine*"'
    """
    supportApiService = googleapiclient.discovery.build(
        serviceName="cloudsupport",
        version="v2",
        discoveryServiceUrl=f"https://cloudsupport.googleapis.com/$discovery/rest?version=v2",
    )

    request = supportApiService.caseClassifications().search(query=query)
    print(request.execute())


# [END cloudsupport_search_case_classifications]

if __name__ == "__main__":
    caseClassifications_search(query='display_name:"*Compute Engine*"')
