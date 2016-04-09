from django.conf.urls import patterns, include, url
from vilogged.api.v1.user.views import *

urlpatterns = [
    url(r'^$', UserList.as_view()),
    url(r'^(?P<_id>\w+)/?$', UserDetail.as_view()),
]