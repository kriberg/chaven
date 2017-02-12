from django.conf.urls import url
from .views import EVESSOConfigView

urlpatterns = [
    url(r'^evessoconfig/$', EVESSOConfigView.as_view(), name='login_evessoconfig'),
    ]
