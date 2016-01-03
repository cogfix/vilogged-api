from core.config_manager import ConfigManager
from django.http import HttpResponse
from django.views.generic import View
import json

class DefaultView(View):

    def get(self, request, **kwargs):
        config = ConfigManager().get_config('system')
        return HttpResponse(json.dumps(config), content_type='application/json')