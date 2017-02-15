from django.conf import settings
import requests
import json


class EVESSO(object):
    token_url = 'https://login.eveonline.com/oauth/token'
    verify_url = 'https://login.eveonline.com/oauth/verify'

    def get_token(self, code):
        response = requests.post(self.token_url,
                                 data={
                                     'grant_type': 'authorization_code',
                                     'code': code
                                 },
                                 auth=(settings.CHAVEN_CLIENT_ID,
                                       settings.CHAVEN_SECRET_KEY))
        response.raise_for_status()
        bearer = json.loads(response.content)
        return bearer.get('access_token')

    def verify_token(self, access_token):
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        response = requests.get(self.verify_url, headers=headers)
        response.raise_for_status()
        token_info = json.loads(response.content)
        return token_info