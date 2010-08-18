import urlparse
import oauth2 as oauth
import httplib2
import urllib
import simplejson

try:
    from urlparse import parse_qs, parse_qsl
except ImportError:
    from cgi import parse_qs, parse_qsl

httplib2.debuglevel = 4
headers = {"user-agent": "jcgregorio-buzz-client",
    'content-type': 'application/x-www-form-urlencoded'
    }

consumer_key = 'anonymous'
consumer_secret = 'anonymous'

request_token_url = 'https://www.google.com/accounts/OAuthGetRequestToken' +
  '?domain=anonymous&scope=https://www.googleapis.com/auth/buzz'
access_token_url = 'https://www.google.com/accounts/OAuthGetAccessToken' +
  '?domain=anonymous&scope=https://www.googleapis.com/auth/buzz'
authorize_url = 'https://www.google.com/buzz/api/auth/OAuthAuthorizeToken' +
  '?domain=anonymous&scope=https://www.googleapis.com/auth/buzz'

consumer = oauth.Consumer(consumer_key, consumer_secret)
client = oauth.Client(consumer)

# Step 1: Get a request token. This is a temporary token that is used for
# having the user authorize an access token and to sign the request to obtain
# said access token.

resp, content = client.request(request_token_url, "POST", headers=headers,
    body="oauth_callback=oob")
if resp['status'] != '200':
  print content
  raise Exception("Invalid response %s." % resp['status'])

request_token = dict(parse_qsl(content))

print "Request Token:"
print "    - oauth_token        = %s" % request_token['oauth_token']
print "    - oauth_token_secret = %s" % request_token['oauth_token_secret']
print

# Step 2: Redirect to the provider. Since this is a CLI script we do not
# redirect. In a web application you would redirect the user to the URL
# below.

base_url = urlparse.urlparse(authorize_url)
query = parse_qs(base_url.query)
query['oauth_token'] = request_token['oauth_token']

print urllib.urlencode(query, True)

url = (base_url.scheme, base_url.netloc, base_url.path, base_url.params,
       urllib.urlencode(query, True), base_url.fragment)
authorize_url = urlparse.urlunparse(url)

print "Go to the following link in your browser:"
print authorize_url
print

# After the user has granted access to you, the consumer, the provider will
# redirect you to whatever URL you have told them to redirect to. You can
# usually define this in the oauth_callback argument as well.
accepted = 'n'
while accepted.lower() == 'n':
    accepted = raw_input('Have you authorized me? (y/n) ')
oauth_verifier = raw_input('What is the PIN? ').strip()


# Step 3: Once the consumer has redirected the user back to the oauth_callback
# URL you can request the access token the user has approved. You use the
# request token to sign this request. After this is done you throw away the
# request token and use the access token returned. You should store this
# access token somewhere safe, like a database, for future use.
token = oauth.Token(request_token['oauth_token'],
    request_token['oauth_token_secret'])
token.set_verifier(oauth_verifier)
client = oauth.Client(consumer, token)

resp, content = client.request(access_token_url, "POST", headers=headers)
access_token = dict(parse_qsl(content))

print "Access Token:"
print "    - oauth_token        = %s" % access_token['oauth_token']
print "    - oauth_token_secret = %s" % access_token['oauth_token_secret']
print
print "You may now access protected resources using the access tokens above."
print

d = dict(
  consumer_key='anonymous',
  consumer_secret='anonymous'
    )

d.update(access_token)

f = open("oauth_token.dat", "w")
f.write(simplejson.dumps(d))
f.close()
