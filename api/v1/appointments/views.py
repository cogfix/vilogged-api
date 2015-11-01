from core.models import Appointments, Visitors, VisitorGroup, Company, Entrance
from core.models import UserProfile, Department
from rest_framework import serializers, generics, mixins, status, permissions
from django.core import serializers as dj_serializer
from rest_framework.response import Response
from utility.utility import Utility, PaginationBuilder
from api.v1.company.views import CompanySerializer
from api.v1.visitor_group.views import VisitorGroupSerializer
from api.v1.department.views import DepartmentSerializer
from api.v1.visitor.views import VisitorSerializer
from api.v1.user.views import UserSerializer
from api.v1.entrance.views import EntranceSerializer
import json
model = Appointments

FILTER_FIELDS = [
    '_id',
    '_rev',
    'visitor',
    'host',
    'representing',
    'purpose',
    'start_date',
    'end_date',
    'start_time',
    'end_time',
    'escort_required',
    'is_approved',
    'is_expired',
    'teams',
    'entrance',
    'created',
    'modified',
    'created_by__name',
    'modified_by__name'
]
SEARCH_FIELDS = [
    'visitor',
    'host',
    'representing',
    'purpose',
    'start_date',
    'end_date',
    'start_time',
    'end_time',
    'escort_required',
    'is_approved',
    'is_expired',
    'teams',
    'entrance'
]

class AppointmentSerializer(serializers.ModelSerializer):

    def validate(self, data):
        return data

    class Meta:
        model = Appointments
        fields = (
            '_id',
            '_rev',
            'visitor',
            'host',
            'representing',
            'purpose',
            'start_date',
            'end_date',
            'start_time',
            'end_time',
            'escort_required',
            'is_approved',
            'is_expired',
            'teams',
            'entrance',
            'created',
            'modified',
            'created_by',
            'modified_by'
        )


class AppointmentList(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, **kwargs):
        model_data = PaginationBuilder().get_paged_data(model, request, FILTER_FIELDS, SEARCH_FIELDS)

        row_list = []
        data = json.loads(dj_serializer.serialize("json", model_data['model_list']))
        for obj in data:
            row = obj['fields']
            row = nest_row(row, obj['pk'])
            row_list.append(row)
        return Response({
            'count': model_data['count'],
            'results': row_list,
            'next': model_data['next'],
            'prev': model_data['prev']
        })


class AppointmentDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView, mixins.CreateModelMixin):
    queryset = model.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    lookup_field = '_id'

    def post_or_put(self, request, *args, **kwargs):
        instance_exists = False
        request.data['_id'] = self.kwargs['_id']
        request.data['entrance'] = Utility.return_id(Entrance, request.data.get('entrance'), 'name')
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
            serializer = AppointmentSerializer(instance)
            row = serializer.data
            row = nest_row(row)
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
    visitor = Utility.get_nested(Visitors, VisitorSerializer, row['visitor'])
    host = Utility.get_nested(UserProfile, UserSerializer, row['host'])
    if len(visitor) > 0 and id is not None:
        del visitor['image']
    if len(host) > 0 and id is not None:
            del host['image']
    row['visitor'] = visitor
    row['host'] = host
    row['entrance'] = Utility.get_nested(Entrance, EntranceSerializer, row['entrance'])
    if type(row['visitor']) is dict and len(row['visitor']) > 0:
        row['visitor']['company'] = Utility.get_nested(Company, CompanySerializer, row['visitor']['company'])
        row['visitor']['group'] = Utility.get_nested(VisitorGroup, VisitorGroupSerializer, row['visitor']['group'])

    if type(row['host']) is dict and len(row['host']) > 0:
        row['host']['department'] = Utility.get_nested(Department, DepartmentSerializer, row['host']['department'])

    return row