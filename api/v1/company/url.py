from django.conf.urls import patterns, include, url
from api.v1.company.views import *

urlpatterns = [
    url(r'^$', CompanyList.as_view()),
    url(r'^(?P<_id>\w+)/?$', CompanyDetail.as_view()),
]