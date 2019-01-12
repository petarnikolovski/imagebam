import uuid
import time
import hashlib
import requests
from fake_useragent import UserAgent


class ImageBam:

    def __init__(self, key, secret):
        """
        :param key: API key provided by ImageBam
        :type key: string
        :param secret: API secret provided by ImageBam
        :type secret: string
        """
        self.key = key
        self.secret = secret
        self.headers = {'Content-Type': 'application/json'}

    def set_fake_user_agent(self):
        """
        Call this method to set HTTP request header to randomly generated
        fake user agent. If the generation of random user agent fails, then
        default to Chrome.
        """
        ua = UserAgent()
        try:
            self.headers['User-Agent'] = ua.random
        except:
            self.headers['User-Agent'] = ua.google

    def generate_oauth_signature(self, *args):
        """
        Generate oauth signature using the MD5. The input arguments must be
        in order that is defined by the API spec. All input arguments must
        be strings!
        """
        sig_data = ''.join([str(arg) for arg in args])
        encoded_sig_data = sig_data.encode('utf-8')
        return hashlib.md5(encoded_sig_data).hexdigest()

    def obtain_unathorized_token(self):
        """
        This method is used to obtain ``oauth_token`` and
        ``oauth_token_secret``.

        :return: Tuple that contains ``oauth_token`` and ``oauth_token_secret``
            in that order
        :rtype: tuple
        """
        oauth_timestamp = int(time.time())
        oauth_nonce = str(uuid.uuid4())

        oauth_signature = self.generate_oauth_signature(
            self.key,
            self.secret,
            oauth_timestamp,
            oauth_nonce
        )

        payload = {
            'oauth_consumer_key': self.key,
            'oauth_nonce': oauth_nonce,
            'oauth_signature': oauth_signature,
            'oauth_signature_method': 'MD5',
            'oauth_timestamp': oauth_timestamp
        }

        url = 'http://www.imagebam.com/sys/oauth/request_token'

        # POST method is not working i.e. ``data=payload``
        r = requests.get(url, params=payload, headers=self.headers)
        # Response is in the form of:
        # oauth_token=XXXXX&oauth_token_secret=XXXXX
        response = r.text
        creds = dict(tuple(e.split('=')) for e in response.split('&'))
        return (creds['oauth_token'], creds['oauth_token_secret'])
