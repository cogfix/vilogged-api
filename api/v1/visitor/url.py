from django.conf.urls import patterns, include, url
from api.v1.visitor.views import *

urlpatterns = [
    url(r'^$', VisitorList.as_view()),
    url(r'^(?P<_id>\w+)/?$', VisitorDetail.as_view()),
]