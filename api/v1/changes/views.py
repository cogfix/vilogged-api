from rest_framework import serializers, generics, mixins, status, permissions, views
from rest_framework.response import Response
from utility.utility import Utility, PaginationBuilder
from django.core import serializers as dj_serializer
import json
from vilogged.models import Changes
model = Changes
FILTER_FIELDS = [
    '_id',
    '_rev',
    'model',
    'type',
    'snapshot',
    'row_id',
    'created'
]
SEARCH_FIELDS = [
    'model',
    'type',
    'row_id'
]

class ChangesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Changes
        fields = (
            '_id',
            '_rev',
            'model',
            'type',
            'row_id',
            'snapshot',
            'created',
        )


class ChangesList(views.APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, **kwargs):
        model_data = PaginationBuilder().get_paged_data(model, request, FILTER_FIELDS, SEARCH_FIELDS, '-created', extra_filters)

        return Response({
            'count': model_data['count'],
            'results': [obj.to_json() for obj in model_data['model_list']],
            'next': model_data['next'],
            'prev': model_data['prev']
        })


class ChangesDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView, mixins.CreateModelMixin):
    queryset = model.objects.all()
    serializer_class = ChangesSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    lookup_field = '_id'

    def post_or_put(self, request, *args, **kwargs):
        request.data['_id'] = self.kwargs['_id']
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
            serializer = ChangesSerializer(instance)
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

def extra_filters(request, list):

    if 'load' in request.query_params:
        load = request.query_params.get('load')

        def updates():
            last_checked = request.query_params.get('last-checked')
            from datetime import datetime
            start_time = datetime.fromtimestamp(float(last_checked) / 1e3)
            data_model = request.query_params.get('model')
            return Changes.objects.filter(
                created__gt=start_time,
                model=data_model
            )

        if load == 'changes':
            return  updates()
    return list