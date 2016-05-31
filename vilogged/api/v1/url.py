from django.conf.urls import patterns, include, url
from vilogged.api.v1.core.views import Messenger

urlpatterns = [
    url(r'^user/?', include('vilogged.api.v1.user.url')),
    url(r'^visitor/?', include('vilogged.api.v1.visitor.url')),
    url(r'^appointment/?', include('vilogged.api.v1.appointments.url')),
    url(r'^appointment-logs/?', include('vilogged.api.v1.appointment_logs.url')),
    url(r'^department/?', include('vilogged.api.v1.department.url')),
    url(r'^visitor-types/?', include('vilogged.api.v1.visitor_types.url')),
    url(r'^company/?', include('vilogged.api.v1.company.url')),
    url(r'^restricted-item/?', include('vilogged.api.v1.restricted_item.url')),
    url(r'^messages/?', include('vilogged.api.v1.messages.url')),
    url(r'^login?', include('vilogged.api.v1.login.url')),
    url(r'^settings/?', include('vilogged.api.v1.settings.url')),
    url(r'^_changes/?', include('vilogged.api.v1.changes.url')),
    url(r'^vehicle/?', include('vilogged.api.v1.vehicle.url')),
    url(r'^messenger/?$', Messenger.as_view()),
]