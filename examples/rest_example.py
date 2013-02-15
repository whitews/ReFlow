import urllib
import urllib2
import getpass
import cookielib
import sys
import json

url = 'http://localhost:8000/login/'
api_url = 'http://localhost:8000/api/'

username = raw_input('Username: ')
password = getpass.getpass('Password: ')

cookie_jar = cookielib.CookieJar()
cookie_handler = urllib2.HTTPCookieProcessor(cookie_jar)

# TODO: change to HTTPSHandler()
opener = urllib2.build_opener(urllib2.HTTPHandler(), cookie_handler)

login_page = opener.open(url)

# We should have some cookies in our cookie jar :)
csrf_cookie = None
for cookie in cookie_jar:
    if cookie.name == 'csrftoken':
        csrf_cookie = cookie
        break

if not csrf_cookie:
    sys.exit()

encoded_args = urllib.urlencode({
    'username': username,
    'password': password,
    'csrfmiddlewaretoken': csrf_cookie.value
})

try:
    opener.open(url, encoded_args)
except urllib2.HTTPError as e:
    print e
    sys.exit()

response = opener.open(api_url)

root_json = response.read()

print json.dumps(json.loads(root_json), indent=4)