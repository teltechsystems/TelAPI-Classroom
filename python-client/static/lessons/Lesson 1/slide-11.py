from lib import create_basic_auth_header
import urllib, urllib2

ACCOUNT_SID = "AC08429a3b19bd48bb8428a900f73eec1f"
AUTH_TOKEN = "50eaa3f902e14cdd8c359bb50894e8b7"
TELAPI_URL = 'https://api.telapi.com/2011-07-01/Accounts/%s/Calls.json' % ACCOUNT_SID

call_data = {}
call_data['To'] = '+15038884341'
call_data['From'] = '+17322761300'
call_data['Url'] = 'http://liveoutput.com/basicCall'

encoded_data = urllib.urlencode(call_data)
request = urllib2.Request(url=TELAPI_URL, data=encoded_data)

auth_header = create_basic_auth_header(ACCOUNT_SID, AUTH_TOKEN)
request.add_header("Authorization", "Basic %s" % auth_header)

print urllib2.urlopen(request).read()