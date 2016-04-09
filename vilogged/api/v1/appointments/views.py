from vilogged.appointments.models import Appointments, AppointmentLogs
from vilogged.department.models import Department
from vilogged.company.models import Company
from vilogged.users.models import UserProfile
from vilogged.entrance.models import Entrance
from vilogged.visitors.models import Visitors, VisitorGroup
from rest_framework import serializers, generics, mixins, status, permissions, views
from django.core import serializers as dj_serializer
from rest_framework.response import Response
from utility.utility import Utility, PaginationBuilder
from vilogged.api.v1.company.views import CompanySerializer
from vilogged.api.v1.visitor_group.views import VisitorGroupSerializer
from vilogged.api.v1.department.views import DepartmentSerializer
from vilogged.api.v1.visitor.views import VisitorSerializer
from vilogged.api.v1.user.views import UserSerializer
from vilogged.api.v1.entrance.views import EntranceSerializer
import json
from datetime import datetime, date
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


class AppointmentList(views.APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, **kwargs):
        model_data = PaginationBuilder().get_paged_data(model, request, FILTER_FIELDS, SEARCH_FIELDS, '-created', extra_filters)

        row_list = []
        for obj in model_data['model_list']:

            row_list.append(obj.to_json())
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
            return Response(instance.to_json(True))

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
    row['status'] = Appointments().get_status(row)
    row['entrance'] = Utility.get_nested(Entrance, EntranceSerializer, row['entrance'])
    if type(row['visitor']) is dict and len(row['visitor']) > 0:
        row['visitor']['company'] = Utility.get_nested(Company, CompanySerializer, row['visitor']['company'])
        row['visitor']['group'] = Utility.get_nested(VisitorGroup, VisitorGroupSerializer, row['visitor']['group'])

    if type(row['host']) is dict and len(row['host']) > 0:
        row['host']['department'] = Utility.get_nested(Department, DepartmentSerializer, row['host']['department'])

    return row


def extra_filters(request, list):
    from django.db.models import Q
    if 'load' in request.query_params:
        load = request.query_params.get('load')
        def in_progress():
            today = date.today()
            checked_in = AppointmentLogs.objects.filter(
                checked_in__year=today.year,
                checked_in__month=today.month,
                checked_in__day=today.day,
                checked_out=None
            ).values_list('_id', flat=True)
            query = dict(_id__in=checked_in)
            if request.query_params.get('host', None) is not None:
                query['host'] = request.query_params['host']
            return Appointments.objects.filter(**query)

        def upcoming():
            today = date.today()
            query = [
                Q(start_date__gte=today) | Q(start_date__lte=today),
                Q(end_date__gte=today),
                Q(is_expired=False),
                Q(is_approved=True)
            ]
            if request.query_params.get('host', None) is not None:
                query.append(Q(host=request.query_params['host']))
            return Appointments.objects.filter(*query)

        def awaiting():
            today = date.today()
            query = [
                Q(start_date__gte=today) | Q(start_date__lte=today),
                Q(end_date__gte=today),
                Q(is_expired=False),
                Q(is_approved=None)
            ]
            if request.query_params.get('host', None) is not None:
                query.append(Q(host=request.query_params['host']))
            return Appointments.objects.filter(*query)

        def rejected():
            today = date.today()
            query = dict(
                is_approved=False,
                end_date__gt=today
            )
            if request.query_params.get('host', None) is not None:
                query['host'] = request.query_params['host']
            return Appointments.objects.filter(**query)

        if load == 'upcoming':
            return  upcoming()
        if load == 'pending':
            return awaiting()
        if load == 'rejected':
            return rejected()
        if load == 'in-progress':
            return  in_progress()

    return list