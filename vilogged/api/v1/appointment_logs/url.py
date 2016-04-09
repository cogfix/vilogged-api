from django.conf.urls import patterns, include, url
from vilogged.api.v1.appointment_logs.views import *

urlpatterns = [
    url(r'^$', AppointmentLogList.as_view()),
    url(r'^(?P<_id>\w+)/?$', AppointmentLogDetail.as_view()),
]