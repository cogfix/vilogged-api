from django.conf.urls import patterns, include, url
from vilogged.api.v1.visitor_types.views import *

urlpatterns = [
    url(r'^$', VisitorTypeList.as_view()),
    url(r'^(?P<_id>\w+)/?$', VisitorTypesDetail.as_view()),
]