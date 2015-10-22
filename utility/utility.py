from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.db.models import Q
import urllib
import urllib2
import base64
import uuid
import json
import re
import threading
from datetime import datetime

class Utility(object):

    @staticmethod
    def error_to_json(error):
        error_dict = {}
        for k in error:
            error_dict[k] = error[k]

        return json.dumps(error_dict)

    @staticmethod
    def send_email(mail_title, message, recipients):
        email = ''
        return send_mail(mail_title, message, email, recipients, fail_silently=False)

    @staticmethod
    def sms(sms_api=None, params=None):

        data = urllib.urlencode(params)
        req = urllib2.Request(sms_api, data)
        return urllib2.urlopen(req)

    @staticmethod
    def load_image_bin(filename):
        with open(filename, "rb") as imageFile:
            new_name = base64.b64encode(imageFile.read())
        return new_name

    @staticmethod
    def get_or_update_rev(rev):

        if rev is None or rev == '':
            rev = '{}'.format(uuid.uuid4()).replace('-', '')
            rev = '1-{}'.format(rev)
        else:
            count = rev.split('-')
            count = int(count[0]) + 1
            new_rev = '{}'.format(uuid.uuid4()).replace('-', '')
            rev = '{0}-{1}'.format(count, new_rev)

        return rev

    @staticmethod
    def get_data_or_none(model, request, **kwargs):
        id = kwargs['_id']
        data = None
        try:
            data = model.objects.get(_id=id)
        except model.DoesNotExist:
            data = None

        return data

    @staticmethod
    def return_id(model, object, unique_field):
        id = None
        params = {}
        if object is not None and object != '' and type(object) is dict and len(object) > 0:
            if object.get('_id', None) is not None:
                unique_field = object.get('_id')
            params[unique_field] = object[unique_field]
            instance = model.objects.filter(**params)
            if len(instance) > 0:
                id = instance[0]._id
            else:
                object['created'] = datetime.now()
                instance = model(**object).save()
                id = instance._id
        if type(object) is str or type(object) is unicode:
            id = object
        return id

    @staticmethod
    def get_nested(instance, instance_serializer, field):
        _instance = {}
        if field is not None:
            try:
                _instance = instance.objects.get(_id=field)
                _instance = instance_serializer(_instance).data
            except instance.DoesNotExist:
                pass

        return _instance

    @staticmethod
    def normalize_query(query_string, findterms=re.compile(r'"([^"]+)"|(\S+)').findall, normspace=re.compile(r'\s{2,}').sub):

        return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]

    @staticmethod
    def get_query(query_string, search_fields):
        ''' Returns a query, that is a combination of Q objects. That combination
            aims to search keywords within a model by testing the given search fields.

        '''
        query = None # Query to search for every search term
        terms = Utility.normalize_query(query_string)
        for term in terms:
            or_query = None # Query to search for a given term in each field
            for field_name in search_fields:
                q = Q(**{"%s__icontains" % field_name: term})
                if or_query is None:
                    or_query = q
                else:
                    or_query = or_query | q
            if query is None:
                query = or_query
            else:
                query = query & or_query
        return query

    @staticmethod
    def build_query(model, request, order_field, search_fields):
        query_string = ''
        found_entries = None
        if ('q' in request.query_params) and request.query_params['q'].strip():
            query_string = request.query_params['q']
            search_fields = Utility.filter_search_field(request, search_fields)
            entry_query = Utility.get_query(query_string, search_fields)
            found_entries = model.objects.filter(entry_query).order_by(order_field)

        return found_entries

    @staticmethod
    def build_filter(fields=None, url_params=None):
        query = {}
        for key in url_params:
            src_key = key
            clean_field = Utility.clean_field(key)
            if clean_field in fields:
                key = Utility.transform_field(key)
                query['{}'.format(key)] = url_params[src_key]

        return query

    @staticmethod
    def transform_field(field):
        src_field = field
        field = field.replace('.', '__').replace('-', '__')
        field = '{}__exact'.format(field)
        f_arr = src_field.split('-')
        if len(f_arr) > 1:
            q = f_arr.pop()
            if q == 'ne':
                 field = field.replace('__exact', '')

        return field

    @staticmethod
    def clean_field(field):
        field = field.replace('.', '__').replace('-lte', '').replace('-gte', '').replace('-lte', '').replace('-lt', '').replace('-gt', '').replace('-ne', '')
        return field

    @staticmethod
    def filter_search_field(request, search_fields):
        if 'only-fields' in request.query_params:
            search_fields = request.query_params['only-fields'].split(',')
        return search_fields



class PaginationBuilder(object):

    def get_paged_data(self, model, request, filter_fields, search_fields, def_order_by='-created'):
        query = Utility.build_filter(filter_fields, request.query_params)

        order_by = request.query_params.get('order_by', def_order_by)
        _model_list = model.objects.filter(**query).order_by(order_by)
        if ('q' in request.query_params) and request.query_params['q'].strip():
            _model_list = Utility.build_query(model, request, order_by, search_fields)
        limit = int(request.query_params.get('limit', 10))
        next = None
        prev = None
        count = None
        if request.query_params.get('page', 1) != 'all':

            page = int(request.query_params.get('page', 1))
            paginator = Paginator(_model_list, limit)
            count = paginator.count
            if page > 1:
                prev = page - 1

            try:
                model_list = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                model_list = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                model_list = paginator.page(paginator.num_pages)
            if model_list.has_next():
                next = model_list.next_page_number()
            if model_list.has_previous():
                prev = model_list.previous_page_number()
        else:
            model_list = _model_list

        return {
            'model_list': model_list,
            'count': count,
            'next': next,
            'prev': prev
        }

class Cron(object):

    def set_interval(self, func, sec):
        def func_wrapper():
            self.set_interval(func, sec)
            func()
        t = threading.Timer(sec, func_wrapper)
        t.start()
        return t