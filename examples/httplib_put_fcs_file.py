import httplib
import getpass
import os
import stat
import json
import sys

host = "localhost:8000"
auth_token_url = "/api-token-auth/"
url = "/api/samples/"

username = raw_input('Username: ')
password = getpass.getpass('Password: ')

# now get token and destroy the user credentials
BOUNDARY = '----Boundary'
content_type = 'multipart/form-data; boundary=%s' % BOUNDARY

auth_headers = {
    'User-Agent': 'python',
    'Content-Type': content_type,
}

auth_data = [
    '--%s' % BOUNDARY,
    'Content-Disposition: form-data; name="username"',
    '',
    username,
    '--%s' % BOUNDARY,
    'Content-Disposition: form-data; name="password"',
    '',
    password,
    '--' + BOUNDARY + '--',
    '',
]

conn = httplib.HTTPConnection(host)
conn.request('POST', auth_token_url, '\r\n'.join(auth_data), auth_headers)
response = conn.getresponse()

token = None

if response.status == 200:
    try:
        data = response.read()
        json_resp = json.loads(data)
        if json_resp.has_key('token'):
            token = json_resp['token']
            # delete all the user credentials
            del(data, json_resp, response, username, password)
        else:
            raise Exception("Authentication token not in response")
    except Exception, e:
        print e
        sys.exit()
else:
    sys.exit("Authentication failed (%s: %s)" % (response.status, response.reason))

if not token:
    sys.exit("No token found")

print "Authentication succeeded, token obtained"
print "----"
subject_pk = raw_input('Subject Primary Key: ')
file_path = raw_input('FCS File Path: ')
file_obj = open(file_path, "rb")

headers = {
    'User-Agent': 'python',
    'Content-Type': content_type,
    'Authorization': "Token %s" % token,
}

body = []
body.append('--' + BOUNDARY)

# add the subject field and value to body
body.append('Content-Disposition: form-data; name="subject"')
body.append('')
body.append(subject_pk)

# get FCS file and append to body
file_size = os.fstat(file_obj.fileno())[stat.ST_SIZE]
filename = file_obj.name.split('/')[-1]
body.append('--%s' % BOUNDARY)
body.append('Content-Disposition: form-data; name="sample_file"; filename="%s"' % filename)
body.append('Content-Type: application/octet-stream')
file_obj.seek(0)
body.append('\r\n' + file_obj.read())

body.append('--' + BOUNDARY + '--')
body.append('')

conn = httplib.HTTPConnection(host)
conn.request('POST', url, '\r\n'.join(body), headers)
response = conn.getresponse()

data = response.read()

print "Response: ", response.status, response.reason
print 'Data: '
print json.dumps(json.loads(data), indent=4)
