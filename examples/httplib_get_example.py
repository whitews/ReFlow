import httplib
import base64

import getpass
import cookielib
import sys
import json

host = 'localhost:8000'
url = '/api/'

username = raw_input('Username: ')
password = getpass.getpass('Password: ')

# Encode the username and password to base64
auth = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')

conn = httplib.HTTPConnection(host)
conn.putrequest("GET", url)
conn.putheader("Authorization", "Basic %s" % auth)
conn.endheaders() # this will connect to the server

# get the response, then the headers and data
response = conn.getresponse()
headers = response.getheaders()
data = response.read()

print "Response: ", response.status, response.reason
print "Headers: ", headers
print 'Data: '
print json.dumps(json.loads(data), indent=4)
