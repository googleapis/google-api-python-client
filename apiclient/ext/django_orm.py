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
