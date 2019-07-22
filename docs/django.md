# Using Django

The Google APIs Client Library for Python has special support for the [Django](https://www.djangoproject.com/) web framework. In particular, there are classes that simplify the OAuth 2.0 protocol steps. This document describes the Django-specific classes available for working with [Flow](https://developers.google.com/api-client-library/python/guide/aaa_oauth#flows), [Credentials](https://developers.google.com/api-client-library/python/guide/aaa_oauth#credentials), and [Storage](https://developers.google.com/api-client-library/python/guide/aaa_oauth#storage) objects.

## Flows

Use the [oauth2client.contrib.django\_orm.FlowField](https://oauth2client.readthedocs.io/en/latest/source/oauth2client.contrib.django_orm.html#oauth2client.contrib.django_orm.FlowField) class as a Django model field so that `Flow` objects can easily be stored. When your application is simultaneously going through OAuth 2.0 steps for many users, it's normally best to store per-user `Flow` objects before the first redirection. This way, your redirection handlers can retrieve the `Flow` object already created for the user. In the following code, a model is defined that allows `Flow` objects to be stored and keyed by `User`:

```py
from django.contrib.auth.models import User
from django.db import models
from oauth2client.contrib.django_orm import FlowField
...
class FlowModel(models.Model):
  id = models.ForeignKey(User, primary_key=True)
  flow = FlowField()
```

## Credentials

Use the [oauth2client.contrib.django\_orm.CredentialsField](https://oauth2client.readthedocs.io/en/latest/source/oauth2client.contrib.django_orm.html#oauth2client.contrib.django_orm.CredentialsField) class as a Django model field so that `Credentials` objects can easily be stored. Similar to `Flow` objects, it's normally best to store per-user `Credentials` objects. In the following code, a model is defined that allows `Credentials` objects to be stored and keyed by `User`:

```py
from django.contrib.auth.models import User
from django.db import models
from oauth2client.contrib.django_orm import CredentialsField
...
class CredentialsModel(models.Model):
  id = models.ForeignKey(User, primary_key=True)
  credential = CredentialsField()
```

## Storage

Use the [oauth2client.contrib.django\_orm.Storage](https://oauth2client.readthedocs.io/en/latest/source/oauth2client.contrib.django_orm.html#oauth2client.contrib.django_orm.Storage) class to store and retrieve `Credentials` objects using a model defined with a `CredentialsField` object. You pass the model, field name for the model key, value for the model key, and field name to the `CredentialsField` constructor. The following shows how to create, read, and write `Credentials` objects using the example `CredentialsModel` class above:

```py
from django.contrib.auth.models import User
from oauth2client.contrib.django_orm import Storage
from your_project.your_app.models import CredentialsModel
...
user = # A User object usually obtained from request.
storage = Storage(CredentialsModel, 'id', user, 'credential')
credential = storage.get()
...
storage.put(credential)
```
