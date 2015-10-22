from django.conf.urls import patterns, include, url
from api.v1.department.views import *

urlpatterns = patterns('',
    url(r'^$', DepartmentList.as_view()),
    url(r'^(?P<_id>\w+)/?$', DepartmentDetail.as_view()),
)