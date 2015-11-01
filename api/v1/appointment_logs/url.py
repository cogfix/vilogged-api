from django.conf.urls import patterns, include, url
from api.v1.appointment_logs.views import *

urlpatterns = patterns('',
    url(r'^$', AppointmentLogList.as_view()),
    url(r'^(?P<_id>\w+)/?$', AppointmentLogDetail.as_view()),
)