import os
import logging
import httplib2

from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from oauth2client.django_orm import Storage
from oauth2client.client import OAuth2WebServerFlow
from django_sample.buzz.models import CredentialsModel
from django_sample.buzz.models import FlowModel
from apiclient.discovery import build

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

STEP2_URI = 'http://localhost:8000/auth_return'
FLOW = OAuth2WebServerFlow(
    client_id='837647042410.apps.googleusercontent.com',
    client_secret='+SWwMCL9d8gWtzPRa1lXw5R8',
    scope='https://www.googleapis.com/auth/buzz',
    user_agent='buzz-django-sample/1.0',
    )

@login_required
def index(request):
  storage = Storage(CredentialsModel, 'id', request.user, 'credential')
  credential = storage.get()
  if credential is None or credential.invalid == True:

    authorize_url = FLOW.step1_get_authorize_url(STEP2_URI)
    f = FlowModel(id=request.user, flow=FLOW)
    f.save()
    return HttpResponseRedirect(authorize_url)
  else:
    http = httplib2.Http()
    http = credential.authorize(http)
    service = build("buzz", "v1", http=http)
    activities = service.activities()
    activitylist = activities.list(scope='@consumption',
                                   userId='@me').execute()
    logging.info(activitylist)

    return render_to_response('buzz/welcome.html', {
                'activitylist': activitylist,
                })


@login_required
def auth_return(request):
    try:
      f = FlowModel.objects.get(id=request.user)
      credential = f.flow.step2_exchange(request.REQUEST)
      storage = Storage(CredentialsModel, 'id', request.user, 'credential')
      storage.put(credential)
      f.delete()
      return HttpResponseRedirect("/")
    except FlowModel.DoesNotExist:
      pass
