from django.db import models


class CredentialsField(models.Field):

  __metaclass__ = models.SubfieldBase

  def db_type(self):
    return 'VARCHAR'

  def to_python(self, value):
    if value is None:
      return None
    if isinstance(value, oauth2client.Credentials):
      return value
    return pickle.loads(base64.b64decode(value))

  def get_db_prep_value(self, value):
    return base64.b64encode(pickle.dumps(value))


class FlowField(models.Field):

  __metaclass__ = models.SubfieldBase

  def db_type(self):
    return 'VARCHAR'

  def to_python(self, value):
    print "In to_python", value
    if value is None:
      return None
    if isinstance(value, oauth2client.Flow):
      return value
    return pickle.loads(base64.b64decode(value))

  def get_db_prep_value(self, value):
    return base64.b64encode(pickle.dumps(value))
