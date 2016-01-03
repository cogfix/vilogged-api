from django.db import models
from rest_framework.authtoken.models import Token
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
import uuid
from datetime import date, datetime
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.db.models import Lookup
import json
import time

list_of_models = (
    'UserProfile',
    'Department',
    'Vehicles',
    'Entrance',
    'VisitorGroup',
    'Company',
    'Visitors',
    'Appointments',
    'AppointmentLogs',
    'MessageQueue',
    'Changes',
    'RestrictedItems',
)

class NotEqual(Lookup):
    lookup_name = 'ne'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return '%s <> %s' % (lhs, rhs), params

from django.db.models.fields import Field
Field.register_lookup(NotEqual)

# Create your models here.

class Department(models.Model):
    _id = models.CharField(max_length=100, unique=True,  primary_key=True)
    _rev = models.CharField(max_length=100,  unique=True, editable=False)
    name = models.CharField(max_length=100, unique=True)
    floor = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100)
    modified_by = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        app_label = 'core'

    def __unicode__(self):
        return '{}'.format(self.name)

    @classmethod
    def model_fields(cls):
        return ['name', 'floor', 'description']


class UserProfile(AbstractUser, models.Model):
    _id = models.CharField(max_length=100,  unique=True,  primary_key=True)
    _rev = models.CharField(max_length=100,  unique=True, editable=False)
    gender = models.CharField(max_length=10, default='Male')
    phone = models.CharField(max_length=20, unique=True)
    home_phone = models.CharField(max_length=20, blank=True, null=True)
    work_phone = models.CharField(max_length=20, blank=True, null=True)
    department = models.ForeignKey(Department, null=True, blank=True)
    designation = models.CharField(max_length=50, blank=True, null=True)
    image = models.TextField(blank=True, null=True)

    class Meta:
        app_label = 'core'

    def __unicode__(self):
        return '{}'.format(self.username)

    @classmethod
    def model_fields(cls):
        return ['first_name', 'last_name', 'description']


class Entrance(models.Model):
    _id = models.CharField(max_length=100, unique=True, primary_key=True)
    _rev = models.CharField(max_length=100,  unique=True, editable=False)
    name = models.CharField(max_length=50, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, blank=True, null=True)
    modified_by = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        app_label = 'core'

    def __unicode__(self):
        return '{}'.format(self.name)


class VisitorGroup(models.Model):
    _id = models.CharField(max_length=100, unique=True, primary_key=True)
    _rev = models.CharField(max_length=100,  unique=True, editable=False)
    name = models.CharField(max_length=50, unique=True)
    black_listed = models.BooleanField(default=False)
    params = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now=True)
    modified = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, blank=True, null=True)
    modified_by = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        app_label = 'core'

    def __unicode__(self):
        return '{0}'.format(self.name)


class Company(models.Model):
    _id = models.CharField(max_length=100, unique=True, primary_key=True)
    _rev = models.CharField(max_length=100,  unique=True, editable=False)
    name = models.CharField(max_length=50, unique=True)
    address = models.CharField(max_length=256)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='co_created_by')
    modified_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='co_modified_by')

    class Meta:
        app_label = 'core'

    def __unicode__(self):
        return '{0}'.format(self.name)


class Visitors(models.Model):
    _id = models.CharField(max_length=100, unique=True, primary_key=True)
    _rev = models.CharField(max_length=100,  unique=True, editable=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50, blank=True, null=True)
    gender = models.CharField(max_length=7, default='Male')
    phone = models.CharField(max_length=20, unique=True, verbose_name='visitors phone number')
    occupation = models.CharField(max_length=50, blank=True, null=True)
    company = models.ForeignKey(Company, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=20, blank=True, null=True)
    state_of_origin = models.CharField(max_length=50, blank=True, null=True)
    lga_of_origin = models.CharField(max_length=50, blank=True, null=True)
    image = models.TextField(blank=True, null=True)
    fingerprint = models.TextField(blank=True, null=True)
    signature = models.TextField(blank=True, null=True)
    pass_code = models.CharField(max_length=50, blank=True, null=True)
    group = models.ForeignKey(VisitorGroup, related_name='group', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='created_by')
    modified_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='modified_by')

    class Meta:
        app_label = 'core'

    def __unicode__(self):
        return '{0} {1}'.format(self.first_name, self.last_name)


class Appointments(models.Model):
    REJECTED = 0
    UPCOMING = 1
    PENDING = 2
    EXPIRED = 3
    IN_PROGRESS = 4

    _id = models.CharField(max_length=100, unique=True, primary_key=True)
    _rev = models.CharField(max_length=100,  unique=True, editable=False)
    visitor = models.ForeignKey(Visitors, related_name="visitor")
    host = models.ForeignKey(UserProfile, blank=True, null=True, related_name="host")
    representing = models.CharField(max_length=100, blank=True, null=True)
    purpose = models.CharField(max_length=50, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    escort_required = models.BooleanField(default=False)
    is_approved = models.NullBooleanField(default=None, null=True, blank=True)
    is_expired = models.BooleanField(default=False)
    teams = models.TextField(null=True, blank=True)
    entrance = models.ForeignKey(Entrance, blank=True, null=True, related_name="entrance")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='app_created_by')
    modified_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='app_modified_by')

    def get_status (self, item):
        today = date.today()
        if item['is_expired']:
            return self.EXPIRED
        if item['is_approved'] and today <= item['start_date']:
            activities = AppointmentLogs.objects.filter(
                    appointment=item['_id'],
                    checked_out=None,
                    checked_in__year=today.year,
                    checked_in__month=today.month,
                    checked_in__day=today.day,
            )
            if len(activities) > 0:
                return self.IN_PROGRESS
            return self.UPCOMING
        if item['is_approved'] is False:
            return self.REJECTED
        if item['is_approved'] is None:
            return self.PENDING

    def set_expired(self):

        active_appointment = Appointments.objects.filter(is_expired=False)
        if len(active_appointment) > 0:
            today = date.today()
            for appointment in active_appointment:
                if today > appointment.end_time:
                    appointment.is_expired = True
                    appointment.save()


class Vehicles(models.Model):
    _id = models.CharField(max_length=100, unique=True, primary_key=True)
    _rev = models.CharField(max_length=100,  unique=True, editable=False)
    appointment_id = models.ForeignKey(Appointments, blank=True, null=True, related_name='vehicle')
    license = models.CharField(max_length=50, blank=True)
    model = models.CharField(max_length=50, blank=True, null=True)
    vehicle_type = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(blank=True, null=True, max_length=20)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='ve_created_by')
    modified_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='ve_modified_by')


class MessageQueue(models.Model):
    _id = models.CharField(max_length=100, unique=True, primary_key=True)
    _rev = models.CharField(max_length=100,  unique=True, editable=False)
    message_body = models.TextField()
    destination = models.CharField(max_length=50)
    source = models.CharField(max_length=50)
    subject = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(default=0)
    type = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='me_created_by')
    modified_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='me_modified_by')


class RestrictedItems(models.Model):
    _id = models.CharField(max_length=100, unique=True, primary_key=True)
    _rev = models.CharField(max_length=100,  unique=True, editable=False)
    type = models.CharField(max_length=100)
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=50)
    appointment_id = models.ForeignKey(Appointments, blank=True, null=True, related_name="restricted_items")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='re_created_by')
    modified_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='re_modified_by')


class AppointmentLogs(models.Model):
    _id = models.CharField(max_length=100, unique=True, primary_key=True)
    _rev = models.CharField(max_length=100,  unique=True, editable=False)
    appointment = models.CharField(Appointments, max_length=50, blank=True, null=True)
    checked_in = models.DateTimeField(default=None, blank=True, null=True)
    checked_out = models.DateTimeField(blank=True, null=True)
    label_code = models.CharField(max_length=50, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='log_created_by')
    modified_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='log_modified_by')


class Changes(models.Model):
    _id = models.CharField(max_length=100, unique=True, primary_key=True)
    _rev = models.CharField(max_length=100,  unique=True, editable=False)
    model = models.CharField(max_length=20)
    type = models.CharField(max_length=20)
    row_id = models.CharField(max_length=20)
    rev = models.CharField(max_length=100, blank=True, null=True)
    snapshot = models.TextField(blank=True, null=True)
    reviewed = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)


@receiver(pre_save)
def update_id(sender, instance=None, **kwargs):
    def save_snapshot(sender, instance, **kwargs):
        def get_value(data, field):
            from django.db.models.fields.related import ForeignKey
            if isinstance(field, ForeignKey) and data:
                return getattr(data, '_id', 'no id')
            elif data is not None:
                return data
            else:
                return ''
        if getattr(instance, '_id', None) is not None:
            changed = dict()
            current_record = sender.objects.filter(_id=instance._id)
            if len(current_record) > 0:
                current_record = current_record.first()
                fields = instance._meta.get_fields()
                for field in fields:
                    if field.name not in ['modified_by', 'created_by', '_rev', 'logentry', 'password']:
                        try:
                            current_value = getattr(current_record, field.name)
                            instance_value = getattr(instance, field.name)
                            if current_value != instance_value:
                                changed[field.name] = get_value(current_value, field)
                        except:
                            pass
            if len(changed) > 0:
                model = sender.__name__.lower()
                Changes.objects.create(model=model, type='updated', row_id=instance._id, snapshot=json.dumps(changed))


    if sender.__name__ in list_of_models: # this is the dynamic
        if instance._id is None or instance._id == '':
            instance._id = '{}'.format(uuid.uuid4()).replace('-', '')

        if instance._rev is None or instance._rev == '':
            rev = '{}'.format(uuid.uuid4()).replace('-', '')
            instance._rev = '1-{}'.format(rev)
        else:
            count = instance._rev.split('-')
            count = int(count[0]) + 1
            new_rev = '{}'.format(uuid.uuid4()).replace('-', '')
            instance._rev = '{0}-{1}'.format(count, new_rev)
    if sender.__name__ in list_of_models and sender.__name__ != 'Changes':
        save_snapshot(sender, instance, **kwargs)


@receiver(post_save)
def manage_post(sender, instance=None, created=False, **kwargs):

    ''' Creates a token whenever a User is created '''
    if created and sender.__name__ is 'UserProfile':
        try:
            Token.objects.create(user=instance)
        except:
            pass

    model = sender.__name__.lower()
    if model != 'changes' and sender.__name__ in list_of_models:

        pre_saved = Changes.objects.filter(reviewed=False, model=model, row_id=instance._id)
        if len(pre_saved) > 0:
            pre_saved = pre_saved.first()
            pre_saved.reviewed = True
            pre_saved.save()
        else:
            if created:
                type = 'created'
                snapshot = serialize_model_instance(instance)
            else:
                type = 'updated'
                snapshot = dict()
            Changes.objects.create(model=model, type=type, row_id=instance._id, reviewed=True, rev=instance._rev, snapshot=json.dumps(snapshot))

@receiver(post_delete)
def manage_delete(sender, instance=None, using=None, **kwargs):

    ''' Creates a token whenever a User is created '''
    try:
        model = sender.__name__.lower()
        type = 'delete'
        if model != 'changes' and sender.__name__ in list_of_models:
            snapshot = json.dumps(serialize_model_instance(instance))
            Changes.objects.create(model=model, type=type, row_id=instance._id, snapshot=snapshot, rev=instance._rev)
    except:
        pass



def serialize_model_instance(instance):
    def get_value(data, field):
        from django.db.models.fields.related import ForeignKey
        if isinstance(field, ForeignKey) and data:
            return getattr(data, '_id', 'no id')
        elif data is not None:
            return data
        else:
            return ''
    fields = instance._meta.get_fields()
    serialized_instance = dict()
    for field in fields:
        if field.name not in ['logentry', 'password']:
            try:
                instance_value = getattr(instance, field.name)
                serialized_instance[field.name] = str(get_value(instance_value, field))
            except AttributeError:
                pass
    return serialized_instance