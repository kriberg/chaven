from django.test import TestCase, override_settings
from rest_framework.test import APIClient


class EVESSOConfigViewTest(TestCase):
    def setUp(self):
        self.api_client = APIClient()

    @override_settings(CHAVEN_CLIENT_ID='123456',
                       CHAVEN_CALLBACK_URL='http://ym/',
                       CHAVEN_TAG_LINE='test')
    def test_auth_config(self):
        response = self.api_client.get('/login/evessoconfig/')
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.data.get('clientID'), '123456'),
        self.assertEquals(response.data.get('callbackURL'), 'http://ym/'),
        self.assertEquals(response.data.get('tagline'), 'test'),
