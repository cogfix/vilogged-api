from vilogged.config_manager import ConfigManager
from rest_framework.response import Response
from django.http import HttpResponse
from django.views.generic import View
from rest_framework import views
from django.contrib.auth.models import Permission, Group
from utility.utility import Utility, PaginationBuilder
from django.core import serializers as dj_serializer
import json
from vilogged.settings import VILOGGED_VERSION
class DefaultView(View):

    def get(self, request, **kwargs):
        config = ConfigManager().get_config('system')
        page_data = dict(
            version=VILOGGED_VERSION,
            author='Musa Musa',
            contact='musa@musamusa.com'
        )
        return HttpResponse(json.dumps(page_data), content_type='application/json')

class UserPermissions(views.APIView):
    model = Permission

    FILTER_FIELDS = [
        'id',
        'name',
        'codename'
    ]

    def get(self, request, **kwargs):
        model_data = PaginationBuilder().get_paged_data(self.model, request, self.FILTER_FIELDS, self.FILTER_FIELDS,
                                                        'id', None, 'all')
        row_list = []
        data = json.loads(dj_serializer.serialize("json", model_data['model_list']))
        for obj in data:
            row = obj['fields']
            row_list.append(row)
        return Response({
            'count': model_data['count'],
            'results': row_list,
            'next': model_data['next'],
            'prev': model_data['prev']
        })



class Messenger(views.APIView):

    def post(self, request):
        type = request.data.get('type', None)
        if type == 'email':
            return self.send_email(request)
        elif type == 'sms':
            return self.send_sms(request)

        return Response({'detail': 'no message type was selected'})


    def send_email(self, request):
        config = ConfigManager().get_config('email')
        to = request.data.get('to', None)
        message = request.data.get('message', None)
        subject = request.data.get('subject', '')
        mail_from = config.get('fromName', 'Online VMS')
        reply_to = config.get('replyTo')
        error = ''

        try:
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText

            me = config.get('user')
            my_password = config.get('password')
            you = to

            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = '{}<{}>'.format(mail_from, config.get('user'))
            msg['To'] = you
            if reply_to:
                msg.add_header('reply-to', reply_to)

            html = '<html><body><p>{}</p></body></html>'.format(message)
            part2 = MIMEText(html, 'html')

            msg.attach(part2)

            # Send the message via gmail's regular server, over SSL - passwords are being sent, afterall
            s = smtplib.SMTP_SSL(config.get('host'))
            # uncomment if interested in the actual smtp conversation
            # s.set_debuglevel(1)
            # do the smtp auth; sends ehlo if it hasn't been sent already
            s.login(me, my_password)
            s.sendmail(me, you, msg.as_string())
            s.quit()
        except smtplib.SMTPException as e:
            errcode = getattr(e, 'smtp_code', -1)
            errmsg = getattr(e, 'smtp_error', 'ignore')
            error = '{} - {}'.format(errcode, errmsg)
        response = 'Message sent successfully'
        if error:
            response = error

        return Response(dict(detail=response))

    def send_sms(self, request):
        config = ConfigManager().get_config('sms')
        to = request.data.get('to', None)
        message = request.data.get('message', None)
        subject = request.data.get('subject', '')


import ldap
class TestUserInsert(View):

    def get(self, request):
        user = None
        error = None
        try:
            l = ldap.initialize("ldap://192.168.1.164:389")

            # Bind/authenticate with a user with apropriate rights to add objects
            l.protocol_version = ldap.VERSION3
            l.set_option(ldap.OPT_REFERRALS, 0)
            l.simple_bind_s("CN=Musa Y. Musa,DC=vilogged,DC=local", "Password1")
        except (ldap.AUTH_UNKNOWN, ldap.CONNECT_ERROR) as e:
            error = e
        except ldap.INVALID_CREDENTIALS as e:
            error = 'Invalid Credentials Provided'
        except ldap.SERVER_DOWN:
            error = 'LDAP Server Down'
        except ldap.LDAPError as e:
            error = e
        else:
            # The dn of our new entry/object
            dn="DC=vilogged,DC=local"

            users = l.search_ext_s(
                dn, ldap.SCOPE_SUBTREE,
                "(sAMAccountName={})".format('musa'),
                attrlist=["sAMAccountName",
                "displayName",
                "mail",
                "distinguishedName",
                "telephoneNumber",
                "ipPhone",
                "home",
                "physicalDeliveryOfficeName",
                "department"
            ])
            user = users[0]

        if user:
            response = user
        else:
            response = error

        return HttpResponse(response, content_type='application/json')
