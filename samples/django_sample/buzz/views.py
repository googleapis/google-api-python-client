import os
import logging
import httplib2

from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django_sample.buzz.models import Credential, Flow
from apiclient.discovery import build
from apiclient.oauth import FlowThreeLegged
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

print os.environ
STEP2_URI = 'http://localhost:8000/auth_return'

@login_required
def index(request):
  try:
    c = Credential.objects.get(id=request.user)
    http = httplib2.Http()
    http = c.credential.authorize(http)
    p = build("buzz", "v1", http=http)
    activities = p.activities()
    activitylist = activities.list(scope='@consumption',
                                   userId='@me').execute()
    logging.info(activitylist)

    return render_to_response('buzz/welcome.html', {
                'activitylist': activitylist,
                })

  except Credential.DoesNotExist:
    p = build("buzz", "v1")
    flow = FlowThreeLegged(p.auth_discovery(),
                   consumer_key='anonymous',
                   consumer_secret='anonymous',
                   user_agent='google-api-client-python-buzz-django/1.0',
                   domain='anonymous',
                   scope='https://www.googleapis.com/auth/buzz',
                   xoauth_displayname='Django Example Web App')

    authorize_url = flow.step1_get_authorize_url(STEP2_URI)
    f = Flow(id=request.user, flow=flow)
    f.save()
    return HttpResponseRedirect(authorize_url)

@login_required
def auth_return(request):
    try:
      f = Flow.objects.get(id=request.user)
      print f
      print f.flow
      print dir(f.flow)
      print type(f.flow)
      credential = f.flow.step2_exchange(request.REQUEST)
      c = Credential(id=request.user, credential=credential)
      c.save()
      f.delete()
      return HttpResponseRedirect("/")
    except Flow.DoesNotExist:
      pass
