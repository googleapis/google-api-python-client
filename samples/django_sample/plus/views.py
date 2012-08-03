import os
import logging
import httplib2

from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from oauth2client.django_orm import Storage
from oauth2client.client import OAuth2WebServerFlow
from django_sample.plus.models import CredentialsModel
from apiclient.discovery import build

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

STEP2_URI = 'http://localhost:8000/oauth2callback'

FLOW = OAuth2WebServerFlow(
    client_id='[[Insert Client ID here.]]',
    client_secret='[[Insert Client Secret here.]]',
    scope='https://www.googleapis.com/auth/plus.me',
    redirect_uri=STEP2_URI,
    user_agent='plus-django-sample/1.0',
    )


@login_required
def index(request):
  storage = Storage(CredentialsModel, 'id', request.user, 'credential')
  credential = storage.get()
  if credential is None or credential.invalid == True:
    authorize_url = FLOW.step1_get_authorize_url()
    return HttpResponseRedirect(authorize_url)
  else:
    http = httplib2.Http()
    http = credential.authorize(http)
    service = build("plus", "v1", http=http)
    activities = service.activities()
    activitylist = activities.list(collection='public',
                                   userId='me').execute()
    logging.info(activitylist)

    return render_to_response('plus/welcome.html', {
                'activitylist': activitylist,
                })


@login_required
def auth_return(request):
  credential = FLOW.step2_exchange(request.REQUEST)
  storage = Storage(CredentialsModel, 'id', request.user, 'credential')
  storage.put(credential)
  return HttpResponseRedirect("/")
