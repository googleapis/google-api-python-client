import pickle
import base64

from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models

from apiclient.ext.django_orm import FlowThreeLeggedField
from apiclient.ext.django_orm import OAuthCredentialsField

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
