import httplib
import base64
import getpass
import os
import stat

host = "localhost:8000"
url = "/api/samples/"

username = raw_input('Username: ')
password = getpass.getpass('Password: ')
subject_pk = raw_input('Subject Primary Key: ')
file_path = raw_input('FCS File Path: ')
file_obj = open(file_path, "rb")

# Encode the username and password to base64
auth = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')

BOUNDARY = '----------Boundary_$'
content_type = 'multipart/form-data; boundary=%s' % BOUNDARY

headers = {
    'User-Agent': 'python_multipart',
    'Content-Type': content_type,
    'Authorization': "Basic %s" % auth,
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
print data
