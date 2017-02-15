from django.conf import settings
from django.http import HttpResponseRedirect
from rest_framework import views
from rest_framework.views import Response
from rest_framework.permissions import AllowAny
from .evesso import EVESSO
from chaven.accounting.authentication import authorize_sso_character, \
    UnauthorizedAccess
from requests.exceptions import HTTPError
import logging


log = logging.getLogger(__name__)


class EVESSOConfigView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        '''
        Gives necessary parameters for authenticating with EVE SSO.
        '''
        return Response({
            'clientID': settings.CHAVEN_CLIENT_ID,
            'callbackURL': settings.CHAVEN_CALLBACK_URL,
            'tagline': settings.CHAVEN_TAG_LINE
        })


class AuthorizeSSOView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        '''
        Performs authentication after redirect from EVE SSO. Creates and sets
        the Authorization header with the JWT payload.
        '''
        code = self.request.query_params.get('code')
        next = self.request.query_params.get('next')

        if code is not None:

            sso = EVESSO()
            try:
                token = sso.get_token(code)
                char = sso.verify_token(token)
            except HTTPError:
                return HttpResponseRedirect('/login?error={}&next={}'.format(
                    'sso',
                    next
                ))
            log.debug('SSO payload {}'.format(char))
            try:
                jwt_token = authorize_sso_character(char)
                log.debug('JWT token {}'.format(jwt_token))
            except UnauthorizedAccess:
                return HttpResponseRedirect('/login?error={}&next={}'.format(
                    'unauthorized',
                    next
                ))
            response = HttpResponseRedirect(next)
            response['Authorization'] = 'JWT {}'.format(jwt_token)
            return response

        return HttpResponseRedirect('/login?error={}&next={}'.format(
            'sso',
            next
        ))
