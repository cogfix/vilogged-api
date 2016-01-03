from django.conf.urls import patterns, include, url
from api.v1.user.views import *

urlpatterns = [

    url(r'^$', AuthUser.as_view()),
]