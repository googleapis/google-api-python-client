import pickle
import base64

from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models

from oauth2client.django_orm import FlowField
from oauth2client.django_orm import CredentialsField

# The Flow could also be stored in memcache since it is short lived.


class FlowModel(models.Model):
  id = models.ForeignKey(User, primary_key=True)
  flow = FlowField()


class CredentialsModel(models.Model):
  id = models.ForeignKey(User, primary_key=True)
  credential = CredentialsField()


class CredentialsAdmin(admin.ModelAdmin):
    pass


class FlowAdmin(admin.ModelAdmin):
    pass


admin.site.register(CredentialsModel, CredentialsAdmin)
admin.site.register(FlowModel, FlowAdmin)
