import urllib
import urllib2
import cookielib
import logging


class GISTokenGenerator:
    def __init__(self, email, password):
        self.cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        self.email = email
        self.login_data = urllib.urlencode({'user[email]': email, 'user[password]': password})

    def generate_token(self):
        logging.info('Generating a token for {0}...'.format(self.email))
        self.opener.open('https://auth.aiesec.org/users/sign_in', self.login_data)
        token = None
        for cookie in self.cj:
            if cookie.name == 'expa_token':
                token = cookie.value
        if token is None:
            raise Exception('Unable to generate a token for {0}!'.format(self.email))
        return token
