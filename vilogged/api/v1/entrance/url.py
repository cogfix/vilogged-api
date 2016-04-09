from django.conf.urls import patterns, include, url
from vilogged.api.v1.entrance.views import *

urlpatterns = [
    url(r'^$', ListView.as_view()),
    url(r'^(?P<_id>\w+)/?$', EntranceDetail.as_view()),
]