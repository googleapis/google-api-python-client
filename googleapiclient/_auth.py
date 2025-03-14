# Copyright 2016 Google Inc. All Rights Reserved.
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

"""Helpers for authentication using oauth2client or google-auth."""

import httplib2

import aiohttp #Team_CKL ADDED CODE
import asyncio #Team_CKL ADDED CODE

try:
    import google.auth
    import google.auth.credentials
    from google.auth.transport.requests import Request as GoogleAuthRequest #Team_CKL ADDED CODE

    HAS_GOOGLE_AUTH = True
except ImportError:  # pragma: NO COVER
    HAS_GOOGLE_AUTH = False

try:
    import oauth2client
    import oauth2client.client

    HAS_OAUTH2CLIENT = True
except ImportError:  # pragma: NO COVER
    HAS_OAUTH2CLIENT = False


async def credentials_from_file(filename, scopes=None, quota_project_id=None): #Team_CKL MODIFIED
    """Returns credentials loaded from a file."""
    if HAS_GOOGLE_AUTH:
        credentials, _ = google.auth.load_credentials_from_file(
            filename, scopes=scopes, quota_project_id=quota_project_id
        )
        return credentials
    else:
        raise EnvironmentError(
            "client_options.credentials_file is only supported in google-auth."
        )


async def default_credentials(scopes=None, quota_project_id=None): #Team_CKL MODIFIED
    """Returns Application Default Credentials."""
    if HAS_GOOGLE_AUTH:
        credentials, _ = google.auth.default(
            scopes=scopes, quota_project_id=quota_project_id
        )
        return credentials
    elif HAS_OAUTH2CLIENT:
        if scopes is not None or quota_project_id is not None:
            raise EnvironmentError(
                "client_options.scopes and client_options.quota_project_id are not supported in oauth2client."
                "Please install google-auth."
            )
        return oauth2client.client.GoogleCredentials.get_application_default()
    else:
        raise EnvironmentError(
            "No authentication library is available. Please install either "
            "google-auth or oauth2client."
        )


async def with_scopes(credentials, scopes): #Team_CKL MODIFIED
    """Scopes the credentials if necessary.

    Args:
        credentials (Union[
            google.auth.credentials.Credentials,
            oauth2client.client.Credentials]): The credentials to scope.
        scopes (Sequence[str]): The list of scopes.

    Returns:
        Union[google.auth.credentials.Credentials,
            oauth2client.client.Credentials]: The scoped credentials.
    """
    if HAS_GOOGLE_AUTH and isinstance(credentials, google.auth.credentials.Credentials):
        return google.auth.credentials.with_scopes_if_required(credentials, scopes)
    else:
        try:
            if credentials.create_scoped_required():
                return credentials.create_scoped(scopes)
            else:
                return credentials
        except AttributeError:
            return credentials


async def authorized_http(credentials): #Team_CKL MODIFIED
    """Returns an http client that is authorized with the given credentials.

    Args:
        credentials (Union[
            google.auth.credentials.Credentials,
            oauth2client.client.Credentials]): The credentials to use.

    Returns:
        aiohttp.ClientSession: An authorized aiohttp client session.
    """
    if HAS_GOOGLE_AUTH and isinstance(credentials, google.auth.credentials.Credentials):
        return aiohttp.ClientSession(auth=GoogleAuthRequest(credentials))
    else:
        headers = await apply_credentials(credentials, {})
        return aiohttp.ClientSession(headers=headers)


async def refresh_credentials(credentials):  #Team_CKL MODIFIED
    """Refreshes the credentials.

    Args:
        credentials (Union[
            google.auth.credentials.Credentials,
            oauth2client.client.Credentials]): The credentials to refresh.
    """
    if HAS_GOOGLE_AUTH and isinstance(credentials, google.auth.credentials.Credentials):
        request = GoogleAuthRequest()
        await credentials.refresh(request)
    else:
        refresh_http = aiohttp.ClientSession()
        await credentials.refresh(refresh_http)
        await refresh_http.close()


async def apply_credentials(credentials, headers): #Team_CKL MODIFIED
    """Applies the credentials to the request headers.

    Args:
        credentials (Union[
            google.auth.credentials.Credentials,
            oauth2client.client.Credentials]): The credentials to apply.
        headers (dict): The request headers.

    Returns:
        dict: The updated headers with credentials applied.
    """
    if not await is_valid(credentials):
        await refresh_credentials(credentials)
    return credentials.apply(headers)


async def is_valid(credentials):  #Team_CKL MODIFIED
    """Checks if the credentials are valid.

    Args:
        credentials (Union[
            google.auth.credentials.Credentials,
            oauth2client.client.Credentials]): The credentials to check.

    Returns:
        bool: True if the credentials are valid, False otherwise.
    """
    if HAS_GOOGLE_AUTH and isinstance(credentials, google.auth.credentials.Credentials):
        return credentials.valid
    else:
        return (
            credentials.access_token is not None
            and not credentials.access_token_expired
        )


async def get_credentials_from_http(http):  #Team_CKL MODIFIED
    """Gets the credentials from the http client session.

    Args:
        http (aiohttp.ClientSession): The http client session.

    Returns:
        google.auth.credentials.Credentials: The credentials.
    """
    if http is None:
        return None
    elif hasattr(http, "credentials"):
        return http.credentials
    else:
        return None
    