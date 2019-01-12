import uuid
import time
import hashlib
import requests
import webbrowser
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

    def authorize_token(self, oauth_token):
        """
        Redirect user to obtain authorization code.

        :param oauth_token: Token obatined from the imagebam (see
            :func:`ImageBam.obtain_unathorized_token`)
        :type oauth_token: string

        This should open a tab in the browser, asking you to accept app
        and copy authorization code.
        """
        url = 'http://www.imagebam.com/sys/oauth/authorize_token'
        webbrowser.open(''.join([url, '?oauth_token=', oauth_token]), new=2)

    def obtain_access_token(
        self, oauth_token, oauth_token_secret, oauth_verifier):
        """
        Obtain access token for the application.

        :param oauth_token: Token obatined from the imagebam (see
            :func:`ImageBam.obtain_unathorized_token`)
        :type oauth_token: string
        :param oauth_token_secret: Token secret obtained from imagebam (see
            :func:`ImageBam.obtain_unathorized_token`)
        :type oauth_token_secret: string
        :param oauth_verifier: Autorization code for the app, obtained by using
            :func:`ImageBam.authorize_token`
        :type oauth_verifier: string
        :return: Tuple that contains ``oauth_token`` and ``oauth_token_secret``
            in that order
        :rtype: tuple
        """
        url = 'http://www.imagebam.com/sys/oauth/request_access_token'

        oauth_timestamp = int(time.time())
        oauth_nonce = str(uuid.uuid4())

        oauth_signature = self.generate_oauth_signature(
            self.key,
            self.secret,
            oauth_timestamp,
            oauth_nonce,
            oauth_token,
            oauth_token_secret
        )

        payload = {
            'oauth_consumer_key': self.key,
            'oauth_nonce': oauth_nonce,
            'oauth_signature': oauth_signature,
            'oauth_signature_method': 'MD5',
            'oauth_timestamp': oauth_timestamp,
            'response_format': 'JSON',
            'oauth_token': oauth_token,
            'oauth_verifier': oauth_verifier,
        }

        r = requests.get(url, params=payload, headers=self.headers)
        response = r.text
        creds = dict(tuple(e.split('=')) for e in response.split('&'))
        return (creds['oauth_token'], creds['oauth_token_secret'])

    def fetch_list_of_images_from_gallery(
        self, oauth_token, oauth_token_secret, gallery_id):
        """
        :param oauth_token: Token obatined from the imagebam (see
            :func:`ImageBam.obtain_access_token`)
        :type oauth_token: string
        :param oauth_token_secret: Token secret obtained from imagebam (see
            :func:`ImageBam.obtain_access_token`)
        :type oauth_token_secret: string
        :param gallery_id: ID of a gallery, ID is located in the gallery url
            e.g. imagebam.com/gallery/ID
        :type gallery_id: string
        :return: List of image urls
        :rtype: list of strings
        """
        url = 'http://www.imagebam.com/sys/API/resource/get_gallery_images'

        oauth_timestamp = int(time.time())
        oauth_nonce = str(uuid.uuid4())

        oauth_signature = self.generate_oauth_signature(
            self.key,
            self.secret,
            oauth_timestamp,
            oauth_nonce,
            oauth_token,
            oauth_token_secret
        )

        payload = {
            'oauth_consumer_key': self.key,
            'oauth_nonce': oauth_nonce,
            'oauth_signature': oauth_signature,
            'oauth_signature_method': 'MD5',
            'oauth_timestamp': oauth_timestamp,
            'response_format': 'JSON',
            'oauth_token': oauth_token,
            'gallery_id': gallery_id
        }

        r = requests.get(url, params=payload, headers=self.headers)
        # If user is not the owner of the gallery, then they cannot access the
        # resource. Example response for failed access:
        # {
        #     "rsp":
        #         {
        #             "status": "fail",
        #             "error_code": 108,
        #             "error_message": "permission denied: gallery_id"
        #         }
        # }
        rsp = r.json()['rsp']
        if rsp['status'] == 'ok':
            return r.json()
        else:
            raise Exception(rsp['error_message'])
