from apiclient.oauth import buzz_discovery, Flow3LO

import simplejson

user_agent = 'google-api-client-python-buzz-cmdline/1.0',
consumer_key = 'anonymous'
consumer_secret = 'anonymous'

flow = Flow3LO(buzz_discovery, consumer_key, consumer_secret, user_agent,
               domain='anonymous',
               scope='https://www.googleapis.com/auth/buzz',
               xoauth_displayname='Google API Client for Python Example App')

authorize_url = flow.step1()

print 'Go to the following link in your browser:'
print authorize_url
print

accepted = 'n'
while accepted.lower() == 'n':
    accepted = raw_input('Have you authorized me? (y/n) ')
pin = raw_input('What is the PIN? ').strip()

access_token = flow.step2_pin(pin)

d = dict(
  consumer_key='anonymous',
  consumer_secret='anonymous'
    )

d.update(access_token)

f = open('oauth_token.dat', 'w')
f.write(simplejson.dumps(d))
f.close()
