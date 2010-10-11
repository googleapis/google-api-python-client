import pickle
import base64

import apiclient.oauth
from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models

# Create your models here.

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

# The Flow could also be stored in memcache since it is short lived.
class Flow(models.Model):
  id = models.ForeignKey(User, primary_key=True)
  flow = FlowThreeLeggedField()

class Credential(models.Model):
  id = models.ForeignKey(User, primary_key=True)
  credential = OAuthCredentialsField()

class CredentialAdmin(admin.ModelAdmin):
    pass

class FlowAdmin(admin.ModelAdmin):
    pass

admin.site.register(Credential, CredentialAdmin)
admin.site.register(Flow, FlowAdmin)
