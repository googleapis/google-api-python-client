# Copyright (C) 2010 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import optparse
import httplib2
import logging
import oauth_wrap
import os
import sys

def load_properties_file(path):
	properties = {}
	for line in open(path):
		line = line.strip()
		if line.startswith('#'):
			continue
			
		key,value = line.split('=')
		properties[key.strip()] = value.strip()
	return properties

def fetch(url):
	logging.debug('Now fetching: %s' % url)
	
	path = os.path.expanduser('~/.oacurl.properties')
	if not os.path.exists(path):
		logging.debug('User is not logged in.')
		
		print 'You are not logged in'
		sys.exit(1)
	properties = load_properties_file(path)
	oauth_parameters = {
		'consumer_key': properties['consumerKey'], 
		'consumer_secret' : properties['consumerSecret'],
		'oauth_token' : properties['accessToken'],
		'oauth_token_secret':properties['accessTokenSecret']}
	
	http = oauth_wrap.get_authorised_http(oauth_parameters)
	response, content = http.request(url)
	logging.debug(response)
	logging.debug(content)
	
	return response,content

def get_command(args):
	if args[0] == 'fetch':
		return 'fetch'
	return None

def configure_logging(options):
	if options.verbose:
	  logging.basicConfig(level=logging.DEBUG)

def main():
	usage = '''Usage: %prog [options] fetch <url>
	Example: %prog -v fetch "https://www.googleapis.com/buzz/v1/people/@me/@self?alt=json&pp=1"
	'''
	parser = optparse.OptionParser(usage=usage)
	parser.set_defaults(verbose=False)
	parser.add_option('-v', '--verbose', action='store_true', dest='verbose')
	parser.add_option('-q', '--quiet', action='store_false', dest='verbose')
	
	(options, args) = parser.parse_args()

	configure_logging(options)
	logging.debug('Options: %s and Args: %s' % (str(options), str(args)))
	
	command = get_command(args)
	
	if not command:
		parser.error('Invalid arguments')
		return
	
	if command == 'fetch':
		response, content = fetch(args[1])
		print response
		print content

if __name__ == '__main__':
	main()