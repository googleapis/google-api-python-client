# Copyright (C) 2010 Google Inc.
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

import apiclient
import base64
import pickle

from django.db import models


class OAuthCredentialsField(models.Field):

  __metaclass__ = models.SubfieldBase

  def db_type(self):
    return 'VARCHAR'

  def to_python(self, value):
    if value is None:
      return None
    if isinstance(value, apiclient.oauth.Credentials):
      return value
    return pickle.loads(base64.b64decode(value))

  def get_db_prep_value(self, value):
    return base64.b64encode(pickle.dumps(value))


class FlowThreeLeggedField(models.Field):

  __metaclass__ = models.SubfieldBase

  def db_type(self):
    return 'VARCHAR'

  def to_python(self, value):
    print "In to_python", value
    if value is None:
      return None
    if isinstance(value, apiclient.oauth.FlowThreeLegged):
      return value
    return pickle.loads(base64.b64decode(value))

  def get_db_prep_value(self, value):
    return base64.b64encode(pickle.dumps(value))
