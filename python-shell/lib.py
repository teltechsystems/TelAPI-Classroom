import base64

def create_basic_auth_header(account_sid, auth_token):
    return base64.encodestring('%s:%s' % (account_sid, auth_token)).replace('\n', '')