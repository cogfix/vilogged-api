from django.conf.urls import patterns, include, url
urlpatterns = [
    url(r'^v1/', include('vilogged.api.v1.url')),
]