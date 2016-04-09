from django.conf.urls import patterns, include, url
from vilogged.api.v1.changes.views import *

urlpatterns = [
    url(r'^$', ChangesList.as_view()),
    url(r'^(?P<_id>\w+)/?$', ChangesDetail.as_view()),
]