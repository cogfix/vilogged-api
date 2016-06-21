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
    'visitor__last_name',
    'visitor__first_name',
    'visitor__phone',
    'visitor__email',
    'visitor__company__name',
    'visitor__type__name',
    'visitor__type__black_listed',
    'host__last_name',
    'host__first_name',
    'host__phone',
    'host__email',
    'is_removed',
    'host__department_name',
    'host__department_floor',
    'host__is_staff',
    'host__is_superuser',
    'host__is_active',
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
    'visitor__first_name',
    'visitor__last_name',
    'host__first_name',
    'host__last_name',
    'representing',
    'purpose',
    'start_date',
    'end_date',
    'start_time',
    'is_removed',
    'end_time',
    'escort_required',
    'is_approved',
    'is_expired',
    'teams'
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
            'is_removed',
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
            row = obj.to_json()
            row['status'] = Appointments().get_status(row)
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
        request.data['_id'] = self.kwargs['_id']
        request.data['entrance'] = Utility.return_id(Entrance, request.data.get('entrance'), 'name')
        request.data['created_by'] = Utility.return_id(UserProfile, request.data.get('created_by'), '_id')
        request.data['modified_by'] = Utility.return_id(UserProfile, request.data.get('modified_by'), '_id')
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
            row = instance.to_json(True)
            row['status'] = Appointments().get_status(row)
            logs = AppointmentLogs().get_logs(row.get('_id'))
            sorted_logs = sorted(logs, key=lambda k: k['created'], reverse=True)
            row['logs'] = sorted_logs
            row['latest'] = sorted_logs[0]
            return Response(row)

    def put(self, request, *args, **kwargs):
        return self.post_or_put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        id = self.kwargs['_id']
        instance = model.objects.get(_id=id)
        instance.is_removed = True
        instance.save()
        return Response(dict(id=instance._id, rev=instance._rev))

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
                checked_out=None,
                is_removed=False
            ).values_list('_id', flat=True)
            query = dict(_id__in=checked_in)
            if request.query_params.get('host', None) is not None:
                query['host'] = request.query_params['host']
            if request.user.is_superuser is not True and request.user.is_staff is not True:
                query['host'] = request.user._id

            return Appointments.objects.filter(**query)

        def upcoming():
            today = date.today()
            query = [
                Q(start_date__gte=today) | Q(start_date__lte=today),
                Q(end_date__gte=today),
                Q(is_expired=False),
                Q(is_approved=True),
                Q(is_removed=False)
            ]
            if request.query_params.get('host', None) is not None:
                query.append(Q(host=request.query_params['host']))
            if request.user.is_superuser is not True and request.user.is_staff is not True:
                query.append(Q(host=request.user._id))
            return Appointments.objects.filter(*query)

        def awaiting():
            today = date.today()
            query = [
                Q(start_date__gte=today) | Q(start_date__lte=today),
                Q(end_date__gte=today),
                Q(is_expired=False),
                Q(is_approved=None),
                Q(is_removed=False)
            ]
            if request.query_params.get('host', None) is not None:
                query.append(Q(host=request.query_params['host']))
            if request.user.is_superuser is not True and request.user.is_staff is not True:
                query.append(Q(host=request.user._id))
            return Appointments.objects.filter(*query)

        def rejected():
            today = date.today()
            query = dict(
                is_approved=False,
                end_date__gt=today,
                is_removed=False
            )
            if request.query_params.get('host', None) is not None:
                query['host'] = request.query_params['host']
            if request.user.is_superuser is not True and request.user.is_staff is not True:
                query['host'] = request.user._id
            return Appointments.objects.filter(**query)

        if load == 'upcoming':
            return  upcoming()
        if load == 'pending':
            return awaiting()
        if load == 'rejected':
            return rejected()
        if load == 'in-progress':
            return  in_progress()
    if 'q' not in request.query_params:
        built_filter = Utility.build_filter(FILTER_FIELDS, request.query_params, model)
        query = dict()
        search_query = []
        if request.user.is_superuser is not True and request.user.is_staff is not True:
            query['host'] = request.user._id
        order_by = request.query_params.get('order_by', '-created').replace('.', '__')
        for key in built_filter:
            if 'search' in request.query_params:
                if key == 'host':
                    search_query.append(Q(**{'host__last_name__icontains': built_filter[key]}) | Q(**{'host__first_name__icontains': built_filter[key]}))
                elif key == 'visitor':
                    search_query.append(Q(**{'visitor__last_name__icontains': built_filter[key]}) | Q(**{'visitor__first_name__icontains': built_filter[key]}))
                else:
                    search_query.append(Q(**{'{}__icontains'.format(key): built_filter[key]}))
            else:
                query['{}__iexact'.format(key)] = built_filter[key]
        try:
            if 'search' in request.query_params:
                list = model.objects.filter(*search_query).order_by(order_by)
            else:
                list = model.objects.filter(**query).order_by(order_by)
        except Exception as e:
            print (e)

    return list