from django.conf.urls import patterns, include, url
from vilogged.api.v1.messages.views import *

urlpatterns = [
    url(r'^$', MessageQueueList.as_view()),
    url(r'^(?P<_id>\w+)/?$', MessageQueueDetail.as_view()),
]