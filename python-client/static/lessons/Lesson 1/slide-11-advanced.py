from lib import create_basic_auth_header
import urllib, urllib2

ACCOUNT_SID = "AC08429a3b19bd48bb8428a900f73eec1f"
AUTH_TOKEN = "50eaa3f902e14cdd8c359bb50894e8b7"
TELAPI_URL = "https://api.telapi.com/2011-07-01/Accounts/%s/Calls.json" % ACCOUNT_SID

def create_call(**call_data):
    encoded_data = urllib.urlencode(call_data)
    request = urllib2.Request(url=TELAPI_URL, data=encoded_data)

    auth_header = create_basic_auth_header(ACCOUNT_SID, AUTH_TOKEN)
    request.add_header("Authorization", "Basic %s" % auth_header)

    return urllib2.urlopen(request).read()

print create_call(To="+15038884341", From="+17322761300", Url="http://liveoutput.com/basicCall")