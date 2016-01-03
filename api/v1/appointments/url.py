from django.conf.urls import patterns, include, url
from api.v1.appointments.views import *

urlpatterns = [
    url(r'^$', AppointmentList.as_view()),
    url(r'^(?P<_id>\w+)/?$', AppointmentDetail.as_view()),
]