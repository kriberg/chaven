from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings

from chaven.schema import schema_view


app_urls = [
    url(r'^login/', include('chaven.login.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^schema/', schema_view, name='chaven_api'),
]


if settings.DEBUG:
    urlpatterns = [url(r'^api/', include(app_urls))]
else:
    urlpatterns = app_urls
