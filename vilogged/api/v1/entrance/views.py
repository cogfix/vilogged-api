from rest_framework import serializers, generics, mixins, views, permissions, status
from django.core import serializers as dj_serializer
from utility.utility import Utility, PaginationBuilder
from rest_framework.response import Response
import json
from vilogged.entrance.models import Entrance
model = Entrance

FILTER_FIELDS = [
    '_id',
    '_rev',
    'name',
    'created',
    'modified',
    'created_by__name',
    'modified_by__name'
]
SEARCH_FIELDS = [
    'name',
    'created_by__name',
    'modified_by__name'
]

class EntranceSerializer(serializers.ModelSerializer):

    def validate(self, data):
        return data

    class Meta:
        model = model
        fields = (
            '_id',
            '_rev',
            'name',
            'created',
            'modified',
            'created_by',
            'modified_by'
        )

model_serializer = EntranceSerializer

class EntranceList(views.APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, **kwargs):
        model_data = PaginationBuilder().get_paged_data(model, request, FILTER_FIELDS, SEARCH_FIELDS, '-created',
                                                        extra_filters)

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


class EntranceDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView, mixins.CreateModelMixin):
    queryset = model.objects.all()
    serializer_class = model_serializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    lookup_field = '_id'

    def post_or_put(self, request, *args, **kwargs):

        request.data['_id'] = self.kwargs['_id']
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
            serializer = model_serializer(instance)
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
    return row

def extra_filters(request, list):
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