from django.conf.urls import patterns, include, url
from api.v1.settings.views import *

urlpatterns = patterns('',
    url(r'^$', ConfigManagerView.as_view()),
    url(r'^(?P<type>\w+)/?$', ConfigManagerView.as_view()),
)