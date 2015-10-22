from rest_framework import serializers, generics, mixins, status, permissions
from rest_framework.response import Response
from utility.utility import Utility, PaginationBuilder
from django.core import serializers as dj_serializer
import json
from user_profile.models import Department
model = Department

FILTER_FIELDS = [
    '_id',
    '_rev',
    'name',
    'floor',
    'modified',
    'created_by__name',
    'modified_by__name'
]
SEARCH_FIELDS = [
    'name',
    'floor',
    'created_by__name',
    'modified_by__name'
]

class DepartmentSerializer(serializers.ModelSerializer):

    def validate(self, data):
        return data

    class Meta:
        model = Department
        fields = (
            '_id',
            '_rev',
            'name',
            'floor',
            'created',
            'modified',
            'created_by',
            'modified_by'
        )
        filter_fields = ('is_approved', 'is_expired', 'checked_in', 'checked_out', 'label_code', 'start_date')



class DepartmentList(generics.ListAPIView):
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


class DepartmentDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView, mixins.CreateModelMixin):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    lookup_field = '_id'

    def post_or_put(self, request, *args, **kwargs):
        user_exists = False
        request.data['_id'] = self.kwargs['_id']
        try:
            user_instance = Department.objects.get(_id=self.kwargs['_id'])
            user_exists = True
        except Department.DoesNotExist:
            user_exists = False

        print (user_exists)

        if user_exists:
            return self.update(request, *args, **kwargs)
        else:
            return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        instance = Utility.get_data_or_none(model, request, **kwargs)
        if instance is None:
            return Response({'detail': 'Not Found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = DepartmentSerializer(instance)
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
    return row