from django.conf.urls import patterns, include, url
from api.v1.restricted_item.views import *

urlpatterns = [
    url(r'^$', RestrictedItemsList.as_view()),
    url(r'^(?P<_id>\w+)/?$', RestrictedItemsDetail.as_view()),
]