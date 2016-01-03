from django.conf.urls import patterns, include, url
from api.v1.visitor_group.views import *

urlpatterns = [
    url(r'^$', VisitorGroupList.as_view()),
    url(r'^(?P<_id>\w+)/?$', VisitorGroupDetail.as_view()),
]