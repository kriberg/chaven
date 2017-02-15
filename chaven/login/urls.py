from django.conf.urls import url
from .views import EVESSOConfigView, AuthorizeSSOView

urlpatterns = [
    url(r'^evessoconfig/$', EVESSOConfigView.as_view(), name='login_evessoconfig'),
    url(r'^authorize/$', AuthorizeSSOView.as_view(), name='login_authorize'),
    ]
