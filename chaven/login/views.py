from django.conf import settings
from rest_framework import views
from rest_framework.views import Response
from rest_framework.permissions import AllowAny


class EVESSOConfigView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, *args, **kwargs):
        return Response({
            'clientID': settings.CHAVEN_CLIENT_ID,
            'callbackURL': settings.CHAVEN_CALLBACK_URL,
            'tagline': settings.CHAVEN_TAG_LINE
        })

