from rest_framework import serializers, generics, mixins
from django.contrib.auth.hashers import make_password
from rest_framework import pagination
from core.models import Visitors
from api.permissions import *
from api.serializer import *

class VisitorSerializer(serializers.ModelSerializer):

    def validate(self, data):
        return data

    class Meta:
        model = Visitors
        fields = (
            '_id',
            '_rev',
            'first_name',
            'last_name',
            'phone',
            'email',
            'gender',
            'address',
            'gender',
            'occupation',
            'company',
            'nationality',
            'date_of_birth',
            'state_of_origin',
            'lga_of_origin',
            'image',
            'fingerprint',
            'signature',
            'pass_code',
            'group',
            'created',
            'modified',
            'created_by',
            'modified_by'
        )
        filter_fields = ('first_name', 'last_name', 'email', 'phone', 'pass_code')



class VisitorList(generics.ListAPIView):
    queryset = Visitors.objects.all()
    serializer_class = VisitorSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    paginate_by = 10
    paginate_by_param = 'limit'
    max_paginate_by = 100


class VisitorDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView, mixins.CreateModelMixin):
    queryset = Visitors.objects.all()
    serializer_class = VisitorSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    lookup_field = '_id'

    def post_or_put(self, request, *args, **kwargs):
        user_exists = False
        request.data['_id'] = self.kwargs['_id']
        try:
            user_instance = Visitors.objects.get(_id=self.kwargs['_id'])
            user_exists = True
        except Visitors.DoesNotExist:
            user_exists = False

        if user_exists:
            return self.update(request, *args, **kwargs)
        else:
            return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.post_or_put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.post_or_put(request, *args, **kwargs)