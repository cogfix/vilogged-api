from django.conf.urls import patterns, include, url
from api.v1.vehicle.views import *

urlpatterns = [
    url(r'^$', VehiclesList.as_view()),
    url(r'^(?P<_id>\w+)/?$', VehiclesDetail.as_view()),
]