from vilogged.config_manager import ConfigManager
from rest_framework.response import Response
from django.http import HttpResponse
from django.views.generic import View
from rest_framework import views
import json

class DefaultView(View):

    def get(self, request, **kwargs):
        config = ConfigManager().get_config('system')
        return HttpResponse(json.dumps(config), content_type='application/json')


class Messenger(views.APIView):

    def post(self, request):
        type = request.data.get('type', None)
        if type == 'email':
            return self.send_email(request)
        elif type == 'sms':
            return self.send_sms(request)

        return Response({'detail': 'no message type was selected'})


    def send_email(self, request):
        from django.core import mail
        from django.core.mail.backends.smtp import EmailBackend
        config = ConfigManager().get_config('email')
        backend = EmailBackend(
            host=config.get('host', 'vms@vilogged.com'),
            port=config.get('port', ''),
            username=config.get('username', 'vms@vilogged.com'),
            password=config.get('password', 'password'),
            use_tls=config.get('use_tls'),
            fail_silently=False,
            use_ssl=config.get('use_ssl'),
            timeout=config.get('timeout'),
            ssl_keyfile=config.get('ssl_keyfile'),
            ssl_certfile=config.get('ssl_certfile')
        )

        to = request.data.get('to', None)
        message = request.data.get('message', None)
        subject = request.data.get('subject', '')
        mail_from = config.get('mailFrom', 'vms@vilogged.com')
        reply_to = [config.get('reply_to', 'vms@vilogged.com')]

        with mail.get_connection(backend='django.core.mail.backends.smtp.EmailBackend') as connection:
            email = mail.EmailMessage(
                subject,
                message,
                mail_from,
                [to],
                [],
                connection=connection,
                reply_to=reply_to
            )
            email.send()
        return Response({})

    def send_sms(self, request):
        config = ConfigManager().get_config('sms')
        to = request.data.get('to', None)
        message = request.data.get('message', None)
        subject = request.data.get('subject', '')
