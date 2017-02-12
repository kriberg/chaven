from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings

app_urls = [
    url(r'^login/', include('chaven.login.urls')),
    url(r'^admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns = [url(r'^api/', include(app_urls))]
else:
    urlpatterns = app_urls
