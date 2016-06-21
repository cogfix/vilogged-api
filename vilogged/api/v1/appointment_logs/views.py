from rest_framework import serializers, generics, mixins, status, permissions, views
from rest_framework.response import Response
from utility.utility import Utility, PaginationBuilder
from django.core import serializers as dj_serializer
import json
from vilogged.users.models import UserProfile
from vilogged.appointments.models import Appointments, AppointmentLogs
from vilogged.api.v1.appointments.views import AppointmentSerializer
from vilogged.api.v1.user.views import UserSerializer
from vilogged.api.v1.visitor.views import VisitorSerializer

model = AppointmentLogs
FILTER_FIELDS = [
    '_id',
    '_rev',
    'appointment',
    'checked_in',
    'checked_out',
    'label_code',
    'modified',
    'created_by',
    'modified_by'
]
SEARCH_FIELDS = [
    'label_code'
]


class AppointmentLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = AppointmentLogs
        fields = (
            '_id',
            '_rev',
            'appointment',
            'checked_in',
            'checked_out',
            'label_code',
            'modified',
            'created_by',
            'modified_by'
        )


class AppointmentLogList(views.APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, **kwargs):
        model_data = PaginationBuilder().get_paged_data(model, request, FILTER_FIELDS, SEARCH_FIELDS, '-created', extra_filters)
        return Response({
            'count': model_data['count'],
            'results': [obj.to_json() for obj in model_data['model_list']],
            'next': model_data['next'],
            'prev': model_data['prev']
        })


class AppointmentLogDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView, mixins.CreateModelMixin):
    queryset = model.objects.all()
    serializer_class = AppointmentLogSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    lookup_field = '_id'

    def post_or_put(self, request, *args, **kwargs):
        request.data['_id'] = self.kwargs['_id']
        request.data['created_by'] = Utility.return_id(UserProfile, request.data.get('created_by'), '_id')
        request.data['modified_by'] = Utility.return_id(UserProfile, request.data.get('modified_by'), '_id')
        try:
            model.objects.get(_id=self.kwargs['_id'])
            return self.update(request, *args, **kwargs)
        except model.DoesNotExist:
            return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        instance = Utility.get_data_or_none(model, request, **kwargs)
        if instance is None:
            return Response({'detail': 'Not Found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = AppointmentLogSerializer(instance)
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
    appointment = Utility.get_nested(Appointments, AppointmentSerializer, row['appointment'])

    if len(appointment) > 0:
        appointment['host'] = Utility.get_nested(UserProfile, UserSerializer, appointment['host'])
        appointment['visitor'] = Utility.get_nested(Visitors, VisitorSerializer, appointment['visitor'])
        del appointment['visitor']['image']
        del appointment['host']['image']
        appointment['log'] = row
        row = appointment
    return row

def extra_filters(request, list):

    if 'load' in request.query_params:
        load = request.query_params.get('load')

    return list