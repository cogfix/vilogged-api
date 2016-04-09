from django.conf.urls import patterns, include, url
from vilogged.api.v1.settings.views import *

urlpatterns = [
    url(r'^$', ConfigManagerView.as_view()),
    url(r'^(?P<type>\w+)/?$', ConfigManagerView.as_view()),
]