from rest_framework import serializers, generics, mixins, views, status, permissions
from rest_framework.response import Response
from utility.utility import Utility
from django.core import serializers as dj_serializer
from core.config_manager import ConfigManager
import json

class ConfigManagerView(views.APIView):

    def get(self, request, **kwargs):
        type = request.query_params.get('type', None)
        config = ConfigManager().get_config(type)
        return Response(config)

class ManageConfig(views.APIView):

    def put_or_post(self, request, **kwargs):
        type = kwargs['type']
        config = ConfigManager().get_config()
        if config.get(type, None) is None:
            status_code = status.HTTP_201_CREATED
        else:
            status_code = status.HTTP_200_OK

        ConfigManager().set_config(request.data, type)

        return Response(ConfigManager().get_config(type), status=status_code)

    def put(self, request, **kwargs):
        return self.put_or_post(request, **kwargs)

    def post(self, request, **kwargs):
        return self.put_or_post(request, **kwargs)
