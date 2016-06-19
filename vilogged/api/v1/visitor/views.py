from rest_framework import serializers, generics, mixins, status, permissions, views
from django.core import serializers as dj_serializer
from rest_framework.response import Response
from vilogged.company.models import Company
from vilogged.visitors.models import Visitors, VisitorGroup
from utility.utility import Utility, PaginationBuilder
from vilogged.api.v1.company.views import CompanySerializer
from vilogged.api.v1.visitor_group.views import VisitorGroupSerializer
import json
model = Visitors

FILTER_FIELDS = [
    '_id',
    '_rev',
    'first_name',
    'last_name',
    'phone',
    'is_removed',
    'email',
    'gender',
    'address',
    'gender',
    'occupation',
    'company',
    'company__name',
    'nationality',
    'date_of_birth',
    'state_of_origin',
    'lga_of_origin',
    'image',
    'fingerprint',
    'signature',
    'pass_code',
    'black_listed',
    'type',
    'type__name',
    'type__black_listed',
    'created',
    'modified',
    'created_by__name',
    'modified_by__name'
]
SEARCH_FIELDS = [
    'first_name',
    'last_name',
    'phone',
    'black_listed',
    'email',
    'gender',
    'is_removed',
    'occupation',
    'nationality',
    'date_of_birth',
    'state_of_origin',
    'lga_of_origin',
    'image',
    'fingerprint',
    'signature',
    'pass_code'
]

class VisitorSerializer(serializers.ModelSerializer):

    def validate(self, data):

        if data.get('email') != '' and data.get('email') is not None:
            email_count = model.objects.filter(email=data['email']).exclude(_id=data['_id'])
            if len(email_count) > 0:
                raise serializers.ValidationError('Email {} already exist'.format(data.get('email')))
        return data

    class Meta:
        model = model
        fields = (
            '_id',
            '_rev',
            'first_name',
            'last_name',
            'phone',
            'email',
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
            'is_removed',
            'pass_code',
            'black_listed',
            'type',
            'created',
            'modified',
            'created_by',
            'modified_by'
        )


class VisitorList(views.APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, **kwargs):
        model_data = PaginationBuilder().get_paged_data(model, request, FILTER_FIELDS, SEARCH_FIELDS, '-created',
                                                        extra_filters)

        row_list = []
        for obj in model_data['model_list']:
            row = obj.to_json()
            row_list.append(row)
        return Response({
            'count': model_data['count'],
            'results': row_list,
            'next': model_data['next'],
            'prev': model_data['prev']
        })


class VisitorDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView, mixins.CreateModelMixin):
    queryset = model.objects.all()
    serializer_class = VisitorSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    lookup_field = '_id'

    def post_or_put(self, request, *args, **kwargs):
        instance_exists = False
        request.data['_id'] = self.kwargs['_id']
        request.data['company'] = Utility.return_id(Company, request.data.get('company', None), 'name')
        try:
            model.objects.get(_id=self.kwargs['_id'])
            instance_exists = True
        except model.DoesNotExist:
            instance_exists = False

        if instance_exists:
            return self.update(request, *args, **kwargs)
        else:
            return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        instance = Utility.get_data_or_none(model, request, **kwargs)
        if instance is None:
            return Response({'detail': 'Not Found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = VisitorSerializer(instance)
            data = serializer.data
            row = nest_row(data)
            return Response(row)

    def put(self, request, *args, **kwargs):
        return self.post_or_put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.post_or_put(request, *args, **kwargs)

def nest_row(row, id=None):
    if id is not None:
        row['_id'] = id
    row['company'] = Utility.get_nested(Company, CompanySerializer, row['company'])
    return row

def extra_filters(request, list):
    if 'q' not in request.query_params:
        built_filter = Utility.build_filter(FILTER_FIELDS, request.query_params, model)
        query = dict()
        order_by = request.query_params.get('order_by', '-created').replace('.', '__')
        for key in built_filter:
            query['{}__iexact'.format(key)] = built_filter[key]
        try:
            list = model.objects.filter(**query).order_by(order_by)
        except Exception as e:
            print (e)
    return list